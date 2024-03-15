import os
import re
import tkinter as tk
from tkinter import filedialog


# 定义函数用于删除注释
def delete_comments_c_java(file_path, delete_empty_line=False):
	"""
	在这个版本的代码中，我们使用了 re.sub() 函数来删除注释。
	正则表达式 //.*
	匹配单行注释，
	而正则表达式 /\*[\s\S]*?\*/
	匹配段落注释。我们将这两种注释都替换为空字符串，从而删除了注释。
	请注意，正则表达式 /\*[\s\S]*?\*/ 中的 [\s\S]
	表示匹配任意字符，包括空白字符和非空白字符。这是因为在 Python 中，正则表达式默认是区分大小写的，
	如果使用 . 来匹配任意字符，那么它不会匹配换行符等非打印字符。
	使用 [\s\S] 则可以解决这个问题
	:param file_path:
	:return:
	"""
	with open(file_path, 'r', encoding='utf-8') as f:
		content = f.read()

	# 删除单行注释
	content = re.sub(r'//.*', '', content)

	# 删除段落注释
	content = re.sub(r'/\*[\s\S]*?\*/', '', content)

	# 删除空行
	if delete_empty_line:
		content = os.linesep.join([s for s in content.splitlines() if s.strip()])

	with open(file_path, 'w', encoding='utf-8') as f:
		f.write(content)


# 定义函数用于删除注释
def delete_comments_py(file_path, delete_empty_line=False):
	"""
	在这个版本的代码中，我们使用了 re.sub() 函数来删除注释。
	正则表达式 #.*
	匹配单行注释，
	而正则表达式 \"\"\"[\s\S]*?\"\"\"
	和正则表达式 \'\'\'[\s\S]*?\'\'\'
	匹配段落注释。我们将这两种注释都替换为空字符串，从而删除了注释。
	请注意，正则表达式 \"\"\"[\s\S]*?\"\"\" 和 \'\'\'[\s\S]*?\'\'\'
	中的 [\s\S] 表示匹配任意字符，包括空白字符和非空白字符。
	:param file_path:
	:return:
	"""
	with open(file_path, 'r', encoding='utf-8') as f:
		content = f.read()

	# 删除单行注释
	content = re.sub(r'#.*', '', content)

	# 删除段落注释
	content = re.sub(r'\"\"\"[\s\S]*?\"\"\"', '', content)
	content = re.sub(r"'''[\s\S]*?'''", '', content)

	# 删除空行
	if delete_empty_line:
		content = os.linesep.join([s for s in content.splitlines() if s.strip()])

	with open(file_path, 'w', encoding='utf-8') as f:
		f.write(content)


if __name__ == '__main__':
	# 弹出窗口让用户选择文件夹
	root = tk.Tk()
	root.withdraw()
	folder_selected = filedialog.askdirectory()

	if folder_selected:
		print("你选择的文件夹是：" + folder_selected)
	else:
		print("你没有选择任何文件夹。")
		exit(0)

	# 支持的文件后缀名
	supported = ['.c', '.java', '.cpp', '.py']

	# 是否删除空行
	delete_empty_line = True

	# 输入要删除注释的文件类型
	file_exts = input(f"请输入要删除注释的文件类型，以空格分隔（如：{' '.join(supported)}）：").split(sep=' ')

	# 判断用户输入是否合法
	for ext in file_exts:
		if ext not in supported:
			file_exts = supported
			print(f"你输入的文件类型 {ext} 不支持，将删除所有支持的文件类型的注释。")
			break

	# 遍历文件夹中的文件
	for root_folder, subfolders, files in os.walk(folder_selected):
		for file_name in files:
			file_ext = os.path.splitext(file_name)[1]
			# 判断文件类型是否符合要求
			if file_ext in file_exts:
				file_path = os.path.join(root_folder, file_name)
				if file_ext == '.c' or file_ext == '.cpp' or file_ext == '.java':
					delete_comments_c_java(file_path, delete_empty_line)
				elif file_ext == '.py':
					delete_comments_py(file_path, delete_empty_line)
				else:
					print(file_name, '不支持的文件！')
				print(file_name, "处理完毕")
