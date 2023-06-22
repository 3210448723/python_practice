import tkinter as tk
from tkinter import filedialog
import os
import subprocess
import re


def get_file_path():
	root = tk.Tk()
	root.withdraw()
	file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
	return file_path


def get_output_file_path():
	root = tk.Tk()
	root.withdraw()
	output_file_path = filedialog.asksaveasfilename(filetypes=[("mp3", "*.mp3"), ("wav", "*.wav")])
	return output_file_path


def get_file_size(file_path):
	return os.path.getsize(file_path)


def compress_audio(file_path, output_file_path, bitrate):
	subprocess.call(['ffmpeg', '-i', file_path, '-ab', bitrate, output_file_path])


def get_bitrate(bitrate_string):
	match = re.search(r'\d+', bitrate_string)
	if match:
		return int(match.group())
	return 0


def main():
	file_path = get_file_path()
	output_file_path = get_output_file_path()

	original_size = get_file_size(file_path)
	print("原始文件大小: {:.2f} MB".format(original_size / (1024 * 1024)))

	options = [
		{"name": "高质量（192 kbps）", "bitrate": "192k"},
		{"name": "中等质量（128 kbps）", "bitrate": "128k"},
		{"name": "低质量（96 kbps）", "bitrate": "96k"}
	]

	print("可选处理方案：")
	for i, option in enumerate(options):
		bitrate = get_bitrate(option["bitrate"])
		estimated_size = original_size * bitrate / (1024 * 1024 * 1024)
		print("{}. {}，预计大小：{:.2f} MB".format(i + 1, option["name"], estimated_size))

	selected_option = int(input("请选择要使用的处理方案（输入序号）：")) - 1
	if selected_option < 0 or selected_option >= len(options):
		print("选择无效！")
		return

	bitrate = options[selected_option]["bitrate"]
	compress_audio(file_path, output_file_path, bitrate)

	compressed_size = get_file_size(output_file_path)
	print("处理后文件大小: {:.2f} MB".format(compressed_size / (1024 * 1024)))
	print("处理完成！")


if __name__ == "__main__":
	main()
