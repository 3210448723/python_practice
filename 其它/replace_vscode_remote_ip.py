#!/usr/bin/env python3
"""Migrate VS Code Remote-SSH workspaces when a server IP changes.

The workspace storage directory is MD5(vscode-remote URI), so changing only
workspace.json loses editor/layout/session state. This script copies the whole
workspace storage tree, rewrites embedded Remote-SSH authorities, migrates the
SQLite state databases, clones SSH host blocks, and keeps a timestamped backup.

Run with VS Code fully closed:
    python replace_vscode_remote_ip.py
    python replace_vscode_remote_ip.py --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Mapping:
    old: str
    new: str


# Add future IP changes here and run this file again.
MAPPINGS = (
    Mapping("100.108.19.27", "100.64.0.5"),
    Mapping("100.86.236.32", "100.64.0.12"),
    Mapping("100.85.91.42", "100.64.0.11"),
)


TEXT_SUFFIXES = {
    ".json",
    ".jsonc",
    ".jsonl",
    ".txt",
    ".log",
    ".code-workspace",
    ".xml",
}


def default_code_user_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "Code" / "User"
    return Path.home() / "AppData" / "Roaming" / "Code" / "User"


def default_ssh_config() -> Path:
    return Path.home() / ".ssh" / "config"


def is_ipv4(value: str) -> bool:
    parts = value.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def workspace_hash(uri: str) -> str:
    return hashlib.md5(uri.encode("utf-8")).hexdigest()


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="")


def compact_remote_authority(host: str, user: str) -> str:
    payload = json.dumps(
        {"hostName": host, "user": user},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return "ssh-remote+" + payload.encode("utf-8").hex()


def rewrite_encoded_authority(text: str, mappings: Iterable[Mapping]) -> str:
    """Rewrite VS Code's hex-encoded ssh-remote authority form too."""

    mapping_by_old = {item.old: item.new for item in mappings}

    def replace_with_separator(match: re.Match[str]) -> str:
        separator = match.group(1)
        token = match.group(2)
        replaced = replace_token(token)
        if replaced == token:
            return match.group(0)
        return "ssh-remote" + separator + replaced

    def replace_token(token: str) -> str:
        try:
            payload = json.loads(bytes.fromhex(token).decode("utf-8"))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            return token

        if isinstance(payload, dict):
            hostname_key = "hostname" if "hostname" in payload else "hostName"
            hostname = payload.get(hostname_key)
        else:
            hostname_key = "hostname"
            hostname = None
        if hostname not in mapping_by_old:
            return token

        updated = dict(payload)
        updated[hostname_key] = mapping_by_old[hostname]
        return json.dumps(
            updated,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8").hex()

    return re.sub(
        r"ssh-remote(\+|%2B)([0-9a-fA-F]+)",
        replace_with_separator,
        text,
        flags=re.IGNORECASE,
    )


def rewrite_references(text: str, mappings: Iterable[Mapping]) -> str:
    updated = text
    for item in mappings:
        # 只替换完整主机令牌；例如 100.85.91.42-ws1 由单独的别名映射处理。
        pattern = re.compile(
            r"(?<![0-9.])" + re.escape(item.old) + r"(?![A-Za-z0-9_.-])"
        )
        updated = pattern.sub(item.new, updated)
    return rewrite_encoded_authority(updated, mappings)


class Migrator:
    def __init__(
        self,
        code_user_dir: Path,
        ssh_config: Path,
        dry_run: bool,
        quarantine_old: bool,
    ) -> None:
        self.code_user_dir = code_user_dir
        self.code_root = code_user_dir.parent
        self.workspace_root = code_user_dir / "workspaceStorage"
        self.ssh_config = ssh_config
        self.dry_run = dry_run
        self.quarantine_old = quarantine_old
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.backup_root = self.code_root / f"remote-ip-migration-backup-{stamp}"
        self.backed_up: set[Path] = set()
        self.changed = False

    def expand_ssh_alias_mappings(
        self, mappings: tuple[Mapping, ...]
    ) -> tuple[Mapping, ...]:
        """Map aliases such as old-ip-ws1 to new-ip-ws1 explicitly."""
        content = read_text(self.ssh_config)
        if content is None:
            return mappings

        hosts = []
        for line in content.splitlines():
            match = re.match(r"^\s*Host\s+(\S+)\s*$", line, re.I)
            if match:
                hosts.append(match.group(1))

        expanded = list(mappings)
        existing = {(item.old, item.new) for item in expanded}
        for item in mappings:
            prefix = item.old + "-"
            for host in hosts:
                if host.startswith(prefix):
                    alias_mapping = Mapping(
                        host,
                        item.new + host[len(item.old):],
                    )
                    if (alias_mapping.old, alias_mapping.new) not in existing:
                        expanded.append(alias_mapping)
                        existing.add((alias_mapping.old, alias_mapping.new))

        return tuple(expanded)

    def backup(self, path: Path, category: str = "CodeUser") -> None:
        if self.dry_run or not path.exists() or path in self.backed_up:
            return
        self.backed_up.add(path)

        try:
            relative = path.relative_to(self.code_user_dir)
            destination = self.backup_root / category / relative
        except ValueError:
            destination = self.backup_root / category / path.name

        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.is_dir():
            shutil.copytree(path, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(path, destination)

    def replace_text_file(self, path: Path, mappings: tuple[Mapping, ...]) -> bool:
        content = read_text(path)
        if content is None:
            return False
        updated = rewrite_references(content, mappings)
        if updated == content:
            return False

        print(f"  text: {path}")
        self.backup(path)
        if not self.dry_run:
            write_text(path, updated)
        self.changed = True
        return True

    def replace_sqlite_file(self, path: Path, mappings: tuple[Mapping, ...]) -> int:
        if not path.is_file():
            return 0

        changed_cells = 0
        try:
            connection = sqlite3.connect(str(path))
        except sqlite3.Error:
            return 0

        try:
            tables = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            for (table,) in tables:
                if table.startswith("sqlite_"):
                    continue
                quoted_table = '"' + table.replace('"', '""') + '"'
                try:
                    columns = [row[1] for row in connection.execute(
                        f"PRAGMA table_info({quoted_table})"
                    ).fetchall()]
                    rows = connection.execute(
                        f"SELECT rowid, * FROM {quoted_table}"
                    ).fetchall()
                except sqlite3.Error:
                    continue

                for row in rows:
                    rowid = row[0]
                    values = row[1:]
                    updates: dict[str, object] = {}
                    for column, value in zip(columns, values):
                        if isinstance(value, str):
                            updated = rewrite_references(value, mappings)
                            if updated != value:
                                updates[column] = updated
                        elif isinstance(value, (bytes, bytearray, memoryview)):
                            try:
                                original = bytes(value).decode("utf-8")
                            except UnicodeDecodeError:
                                continue
                            updated = rewrite_references(original, mappings)
                            if updated != original:
                                updates[column] = updated.encode("utf-8")

                    if updates:
                        assignments = ", ".join(
                            '"' + column.replace('"', '""') + '" = ?'
                            for column in updates
                        )
                        connection.execute(
                            f"UPDATE {quoted_table} SET {assignments} WHERE rowid = ?",
                            [*updates.values(), rowid],
                        )
                        changed_cells += len(updates)

            if changed_cells and not self.dry_run:
                self.backup(path)
                connection.commit()
            elif changed_cells:
                connection.rollback()
        except sqlite3.Error:
            connection.rollback()
            changed_cells = 0
        finally:
            connection.close()

        if changed_cells:
            print(f"  sqlite({changed_cells} cells): {path}")
            self.changed = True
        return changed_cells

    def copy_tree_if_missing(self, source: Path, target: Path) -> bool:
        if target.exists():
            return False
        print(f"  workspace: {source.name} -> {target.name}")
        self.backup(source, "workspaceStorage")
        if not self.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target)
        self.changed = True
        return True

    def migrate_workspace_storage(self, mappings: tuple[Mapping, ...]) -> None:
        if not self.workspace_root.is_dir():
            return

        records: list[tuple[Path, str, str]] = []
        for directory in self.workspace_root.iterdir():
            if not directory.is_dir():
                continue
            workspace_file = directory / "workspace.json"
            if not workspace_file.is_file():
                continue
            content = read_text(workspace_file)
            if content is None:
                continue
            try:
                folder_uri = str(json.loads(content)["folder"])
            except (KeyError, TypeError, json.JSONDecodeError):
                continue
            records.append((directory, directory.name, folder_uri))

        for mapping in mappings:
            for source_dir, source_name, folder_uri in records:
                old_uri: str | None = None
                new_uri: str | None = None

                rewritten_uri = rewrite_references(folder_uri, mappings)
                if rewritten_uri != folder_uri:
                    old_uri = folder_uri
                    new_uri = rewritten_uri
                elif mapping.new in folder_uri:
                    # Handles the earlier partial migration: workspace.json was
                    # changed but its directory still has the old URI hash.
                    candidate_old = folder_uri.replace(mapping.new, mapping.old)
                    if workspace_hash(candidate_old) == source_name:
                        old_uri = candidate_old
                        new_uri = folder_uri

                if not old_uri or not new_uri:
                    continue

                target_dir = self.workspace_root / workspace_hash(new_uri)
                created = self.copy_tree_if_missing(source_dir, target_dir)

                if self.dry_run:
                    continue

                if not target_dir.exists():
                    continue

                target_workspace = target_dir / "workspace.json"
                target_content = read_text(target_workspace)
                if target_content is not None:
                    target_updated = rewrite_references(target_content, mappings)
                    if target_updated != target_content:
                        self.backup(target_workspace, "workspaceStorage")
                        write_text(target_workspace, target_updated)
                        self.changed = True

                # If this was the earlier partial migration, restore the old
                # source identity so the old and new folders remain distinct.
                if mapping.new in folder_uri and mapping.old not in folder_uri:
                    source_workspace = source_dir / "workspace.json"
                    source_content = read_text(source_workspace)
                    if source_content is not None:
                        restored = rewrite_references(
                            source_content.replace(mapping.new, mapping.old),
                            tuple(),
                        )
                        if restored != source_content:
                            self.backup(source_workspace, "workspaceStorage")
                            write_text(source_workspace, restored)
                            self.changed = True

                # Migrate embedded editor/session URIs in the copied workspace
                # without modifying the preserved old workspace tree.
                for child in target_dir.rglob("*"):
                    if not child.is_file():
                        continue
                    if child.name.startswith("state.vscdb"):
                        self.replace_sqlite_file(child, mappings)
                    elif child.suffix.lower() in TEXT_SUFFIXES:
                        self.replace_text_file(child, mappings)

    def migrate_cached_configurations(self, mappings: tuple[Mapping, ...]) -> None:
        root = self.code_root / "CachedConfigurations" / "user"
        if not root.is_dir():
            return

        for source in list(root.iterdir()):
            if not source.is_dir():
                continue
            for mapping in mappings:
                target_name: str | None = None
                direct = f"ssh-remote+{mapping.old}"
                if source.name == direct:
                    target_name = f"ssh-remote+{mapping.new}"
                elif source.name.startswith("ssh-remote+"):
                    encoded = source.name[len("ssh-remote+"):]
                    try:
                        payload = json.loads(bytes.fromhex(encoded).decode("utf-8"))
                    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                        payload = None
                    if (
                        isinstance(payload, dict)
                        and payload.get("hostname", payload.get("hostName"))
                        == mapping.old
                    ):
                        target_name = compact_remote_authority(
                            mapping.new,
                            str(payload.get("user", "")),
                        )

                if target_name is None:
                    continue

                target = root / target_name
                if not target.exists():
                    print(f"  cached config: {source.name} -> {target.name}")
                    self.backup(source, "CachedConfigurations")
                    if not self.dry_run:
                        shutil.copytree(source, target)
                    self.changed = True

                if self.dry_run or not target.exists():
                    continue
                for child in target.rglob("*"):
                    if child.is_file() and child.suffix.lower() in TEXT_SUFFIXES:
                        self.replace_text_file(child, mappings)

    def rewrite_active_cached_configurations(
        self, mappings: tuple[Mapping, ...]
    ) -> None:
        """Rewrite IPs used inside cached settings, including proxy settings."""
        root = self.code_root / "CachedConfigurations" / "user"
        if not root.is_dir():
            return
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                self.replace_text_file(path, mappings)

    def quarantine_legacy_workspace_storage(
        self, mappings: tuple[Mapping, ...]
    ) -> None:
        """Move migrated old workspace identities out of active VS Code storage.

        VS Code discovers project history by enumerating workspaceStorage. Keeping
        the old hashed directories there makes the old server appear in the UI,
        even when active settings already point at the new IP. The old trees are
        moved, not deleted, and remain recoverable under this run's backup.
        """
        if not self.workspace_root.is_dir():
            return

        quarantine_root = self.backup_root / "quarantined-old-workspaceStorage"
        for source_dir in list(self.workspace_root.iterdir()):
            if not source_dir.is_dir():
                continue

            workspace_file = source_dir / "workspace.json"
            content = read_text(workspace_file)
            if content is None:
                continue
            try:
                folder_uri = str(json.loads(content)["folder"])
            except (KeyError, TypeError, json.JSONDecodeError):
                continue

            new_uri = rewrite_references(folder_uri, mappings)
            if new_uri == folder_uri:
                # A previous pass may already have rewritten workspace.json,
                # while leaving the directory under its old URI hash. Detect
                # that case by reversing the mapping and checking the old hash.
                reverse_mappings = tuple(
                    Mapping(item.new, item.old) for item in mappings
                )
                candidate_old = rewrite_references(folder_uri, reverse_mappings)
                if (
                    candidate_old == folder_uri
                    or workspace_hash(candidate_old) != source_dir.name
                ):
                    continue
                new_uri = folder_uri

            target_dir = self.workspace_root / workspace_hash(new_uri)
            target_file = target_dir / "workspace.json"
            target_content = read_text(target_file)
            try:
                target_folder = str(json.loads(target_content or "")["folder"])
            except (KeyError, TypeError, json.JSONDecodeError):
                target_folder = ""

            # Never move an old tree unless its migrated counterpart is present
            # and has the expected new identity.
            if target_dir == source_dir or target_folder != new_uri:
                print(
                    "warning: keep old workspace (new counterpart not verified): "
                    f"{source_dir.name} -> {target_dir.name}"
                )
                continue

            destination = quarantine_root / source_dir.name
            print(f"  quarantine workspace: {source_dir.name} -> {destination}")
            if not self.dry_run:
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    print(f"warning: quarantine target exists, keeping: {source_dir}")
                    continue
                shutil.move(str(source_dir), str(destination))
            self.changed = True

    def rewrite_active_workspace_storage(
        self, mappings: tuple[Mapping, ...]
    ) -> None:
        """Rewrite state/chat files already living under active workspace hashes.

        Chat editing content files often have no extension, so suffix-only scans
        miss them. workspaceStorage is VS Code metadata, not project source code;
        unreadable binary files are skipped by read_text().
        """
        if not self.workspace_root.is_dir():
            return

        for path in self.workspace_root.rglob("*"):
            if not path.is_file():
                continue
            if path.name.startswith("state.vscdb"):
                self.replace_sqlite_file(path, mappings)
            else:
                self.replace_text_file(path, mappings)

    def quarantine_legacy_cached_configurations(
        self, mappings: tuple[Mapping, ...]
    ) -> None:
        """Move stale old Remote-SSH cache entries out of active cache storage."""
        root = self.code_root / "CachedConfigurations" / "user"
        if not root.is_dir():
            return

        def target_name(source: Path) -> str | None:
            for mapping in mappings:
                direct = f"ssh-remote+{mapping.old}"
                if source.name == direct:
                    return f"ssh-remote+{mapping.new}"
                if not source.name.startswith("ssh-remote+"):
                    continue
                encoded = source.name[len("ssh-remote+"):]
                try:
                    payload = json.loads(bytes.fromhex(encoded).decode("utf-8"))
                except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if (
                    isinstance(payload, dict)
                    and payload.get("hostname", payload.get("hostName"))
                    == mapping.old
                ):
                    return compact_remote_authority(
                        mapping.new, str(payload.get("user", ""))
                    )
            return None

        quarantine_root = self.backup_root / "quarantined-CachedConfigurations"
        for source in list(root.iterdir()):
            if not source.is_dir():
                continue
            new_name = target_name(source)
            if new_name is None or not (root / new_name).exists():
                continue

            destination = quarantine_root / source.name
            print(f"  quarantine cached config: {source.name} -> {destination}")
            if not self.dry_run:
                destination.parent.mkdir(parents=True, exist_ok=True)
                if destination.exists():
                    print(f"warning: quarantine target exists, keeping: {source}")
                    continue
                shutil.move(str(source), str(destination))
            self.changed = True

    def update_active_files(self, mappings: tuple[Mapping, ...]) -> None:
        files = (
            self.code_user_dir / "settings.json",
            self.code_user_dir / "globalStorage" / "storage.json",
            self.code_user_dir / "sync" / "settings" / "lastSyncsettings.json",
        )
        for path in files:
            if path.is_file():
                self.replace_text_file(path, mappings)

        databases = [
            self.code_user_dir / "globalStorage" / "state.vscdb",
            *self.workspace_root.glob("*/state.vscdb"),
            *self.workspace_root.glob("*/state.vscdb.backup"),
        ]
        seen: set[Path] = set()
        for database in databases:
            if database not in seen:
                seen.add(database)
                self.replace_sqlite_file(database, mappings)

    def clone_ssh_host_blocks(self, mappings: tuple[Mapping, ...]) -> None:
        if not self.ssh_config.is_file():
            print(f"warning: SSH config not found: {self.ssh_config}")
            return

        content = read_text(self.ssh_config)
        if content is None:
            print(f"warning: cannot decode SSH config: {self.ssh_config}")
            return
        lines = content.splitlines()

        for mapping in mappings:
            new_header = re.compile(r"^\s*Host\s+" + re.escape(mapping.new) + r"\s*$", re.I)
            if any(new_header.match(line) for line in lines):
                continue

            old_header = re.compile(r"^\s*Host\s+" + re.escape(mapping.old) + r"\s*$", re.I)
            try:
                start = next(i for i, line in enumerate(lines) if old_header.match(line))
            except StopIteration:
                print(f"warning: SSH host block not found: {mapping.old}")
                continue

            end = len(lines)
            for i in range(start + 1, len(lines)):
                if re.match(r"^\s*Host\s+", lines[i], re.I):
                    end = i
                    break

            block = [rewrite_references(line, mappings) for line in lines[start:end]]
            block[0] = f"Host {mapping.new}"

            print(f"  ssh: {mapping.old} -> {mapping.new}")
            self.backup(self.ssh_config, "ssh")
            lines.extend([""] + block)
            self.changed = True

        if self.changed and not self.dry_run:
            write_text(self.ssh_config, "\n".join(lines) + "\n")

    def run(self, mappings: tuple[Mapping, ...]) -> None:
        mappings = self.expand_ssh_alias_mappings(mappings)
        self.migrate_workspace_storage(mappings)
        self.migrate_cached_configurations(mappings)
        self.rewrite_active_cached_configurations(mappings)
        self.rewrite_active_workspace_storage(mappings)
        self.update_active_files(mappings)
        self.clone_ssh_host_blocks(mappings)
        if self.quarantine_old:
            self.quarantine_legacy_workspace_storage(mappings)
            self.quarantine_legacy_cached_configurations(mappings)


def vscode_is_running() -> bool:
    if os.name != "nt":
        return False
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Code.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return False
    return '"Code.exe"' in result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="只检查并显示计划，不写文件")
    parser.add_argument("--allow-open", action="store_true", help="允许 VS Code 运行时执行")
    parser.add_argument(
        "--keep-old",
        action="store_true",
        help="保留旧 workspaceStorage/CachedConfigurations；默认将已验证迁移的旧项移到可恢复备份",
    )
    parser.add_argument("--code-user-dir", type=Path, default=default_code_user_dir())
    parser.add_argument("--ssh-config", type=Path, default=default_ssh_config())
    args = parser.parse_args()

    if not args.allow_open and vscode_is_running():
        print("请先完全退出 VS Code，再运行迁移；或者显式使用 --allow-open。", file=sys.stderr)
        return 2

    valid = []
    for mapping in MAPPINGS:
        if not is_ipv4(mapping.new):
            print(f"skip invalid IPv4: {mapping.old} -> {mapping.new}", file=sys.stderr)
        else:
            valid.append(mapping)
    if not valid:
        print("没有可执行的合法映射。", file=sys.stderr)
        return 2

    migrator = Migrator(
        args.code_user_dir,
        args.ssh_config,
        args.dry_run,
        quarantine_old=not args.keep_old,
    )
    migrator.run(tuple(valid))
    print("完成。" if not args.dry_run else "Dry-run 完成，未写入文件。")
    if not args.dry_run:
        print(f"备份目录: {migrator.backup_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
