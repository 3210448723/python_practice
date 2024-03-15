import os
import re
from tkinter import Tk, filedialog, messagebox, simpledialog
from bs4 import BeautifulSoup, NavigableString

def remove_css_js(soup):
    # 移除所有style标签的内容，但保留标签（以便保留文本）
    for style in soup.find_all('style'):
        style.string = ''

    # 移除所有script标签的内容，但保留标签（以便保留文本）
    for script in soup.find_all('script'):
        script.string = ''

    # 移除所有内联样式
    for element in soup.find_all(style=True):
        element.attrs.pop('style', None)

    # 移除所有内联事件处理器（例如 onclick）
    for attr in ['onclick', 'onmouseover', 'onmouseout', 'onload', 'onerror']:
        for element in soup.find_all(True):
            if attr in element.attrs:
                element.attrs.pop(attr, None)

    # 移除所有链接到CSS文件的link标签
    for link in soup.find_all('link', rel=re.compile(r'stylesheet')):
        link.decompose()

    # 移除所有JavaScript文件的引用
    for script in soup.find_all('script', src=True):
        script.decompose()

    # 移除所有内嵌的CSS和JavaScript代码
    for tag in soup.find_all(True):
        if tag.name in ['style', 'script']:
            tag.replace_with(NavigableString(tag.string or ''))

def clean_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as html_file:
        soup = BeautifulSoup(html_file, 'html.parser')

    remove_css_js(soup)

    # 清理后的HTML内容，保留文本
    cleaned_html = str(soup)

    return cleaned_html

def save_cleaned_html(cleaned_html, title='保存清理后的HTML文件'):
    root = Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title=title,
        defaultextension=".html",
        filetypes=(("HTML files", "*.html"), ("All files", "*.*"))
    )

    if not file_path:
        messagebox.showerror("错误", "没有选择保存路径。")
        return None

    try:
        with open(file_path, 'w', encoding='utf-8') as new_html_file:
            new_html_file.write(cleaned_html)
        messagebox.showinfo("成功", "文件已成功保存。")
        return file_path
    except Exception as e:
        messagebox.showerror("错误", f"保存文件时发生错误: {e}")
        return None

def main():
    root = Tk()
    root.withdraw()

    # 选择HTML文件
    file_path = filedialog.askopenfilename(
        title="选择HTML文件",
        defaultextension=".html",
        filetypes=(("HTML files", "*.html"), ("All files", "*.*"))
    )

    if not file_path:
        messagebox.showerror("错误", "没有选择文件。")
        return

    try:
        # 清理HTML文件
        cleaned_html = clean_html_file(file_path)

        # 保存清理后的HTML文件
        export_path = save_cleaned_html(cleaned_html)

        # 如果保存成功，打开保存的文件
        if export_path:
            os.startfile(export_path)
    except Exception as e:
        messagebox.showerror("错误", f"处理文件时发生错误: {e}")

if __name__ == "__main__":
    main()
