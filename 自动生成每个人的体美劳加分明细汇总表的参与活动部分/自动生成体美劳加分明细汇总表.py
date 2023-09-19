# Author:Yuan Jinmin
# -*- coding = utf-8 -*-
# @Time  :2022/9/29 17:01
# @Author:YJM

import csv

import pdfplumber

# 参数列表
# 计科方向名单，可更换
# name_path = r"名单.csv"
# 全年级名单
name_path = r"../全年级名单.csv"
# 完整文件
# text_path = r"2021-2022计算机科学与工程学院活动参与名单.pdf"
# 部分内容，用于测试
text_path = r"2023/2022-2023学年美育、体育、劳育名单（终）.pdf"
# 输出目录
target_path = r"whole.csv"


# 可以不用
def write_csv(target_path, data):
	# 标题（第一行）
	header = ['序号', '班级', '学号', '姓名', '得分（1次10分）', '参与各活动名称']

	# 为了删除多余的空白行，我们可以为 open() 函数指定关键字参数 newline=’’：
	with open(target_path, 'w', encoding='GBK', newline='') as f:
		writer = csv.writer(f)
		# write the header
		writer.writerow(header)
		for d in data:
			# write the data
			writer.writerow(d)


def load_name_list(name_path):
	"""
	加载学生数据集
	:param name_path: 学生名称路径
	:return:  data_list list类型
	"""
	name_list = []

	with open(name_path, encoding="utf-8") as f:
		for line in f:
			line = line.strip("\n")
			# 序号，班级，学号，姓名
			name_list.append(line.split(','))
	# print(name_list)
	return name_list


def read_pdf():
	"""
	把PDF读入内存
	:return: PDF内容
	"""
	with pdfplumber.open(text_path) as pdf:
		# print(pdf.pages)  # 获取pdf文档所有的页，类型是dict
		# 总页数
		total_pages = len(pdf.pages)
		print("total_pages: ", total_pages)

		# page = pdf.pages[0]  # 获取第一页
		# print(type(page))  # <class 'pdfplumber.page.Page'>
		# print(page.extract_text())  #获取第一页的内容

		# fitz读取pdf全文
		content = ""
		for i in range(0, len(pdf.pages)):
			current_page = pdf.pages[i]
			content += current_page.extract_text()
		# 输出当前页文本
		# print(current_page.extract_text())
		# print(current_page.extract_tables())
		# print(content)
	return content


# print(content)

if __name__ == "__main__":
	# 学号列表：序号，班级，学号，姓名
	id_list = load_name_list(name_path)
	# 参与活动记录
	content = read_pdf()
	# 将文本按照活动分割成一个list
	content_splitted_list = content.split("以下学生")
	# print(content_splitted_list)
	# 总共有几个活动，应该是118
	print(len(content_splitted_list))

	# 标题（第一行）
	header = ['序号', '班级', '学号', '姓名', '得分（1次10分）', '参与各活动名称']

	# 为了删除多余的空白行，我们可以为 open() 函数指定关键字参数 newline=’’：
	with open(target_path, 'w', encoding='GBK', newline='') as f:
		writer = csv.writer(f)
		# write the header
		writer.writerow(header)

		# id_info = []
		# 记录每个活动的位置和名称
		for id in id_list:
			# 某人参与的活动列表
			activities = ''
			i = 0
			for item in content_splitted_list:
				# 查询到某人
				if item.find(id[2]) != -1:
					index = item.index("活动")
					# print(index)
					# 截取出 "以下学生{}活动时间：" 大括号中的内容
					activity_name = item[0:index].replace("\n", "").replace(" ", "").replace("2021-2022学年", "").replace(
						"参", "") \
						.replace("与", "").replace("加", "").replace("了", "").replace("我", "").replace("院", "") \
						.replace("校", "").replace("的", "").replace("组织", "").replace("于", "")
					# print(activity_name)
					i += 1
					start = item.index("活动时间：") + 5
					end = item.index("\n", start)
					# 截取出活动时间
					time = item[start:end]
					activities += str(i) + '. ' + time + ' ' + activity_name + '\n'
			# 得分
			id.append(i * 10)
			# 参与活动名称
			id.append(activities)
			# write the data
			writer.writerow(id)
	# print(id_info)

# write_csv(target_path, id_info)
