# -*- coding = utf-8 -*-
# @Time  :2023/6/20 16:50
# @Author:YJM
# @Site  :
# @File  :爬取大数据学习通题库.py
# @Software: IntelliJ IDEA
import re

import requests
from lxml import etree

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
	              'Chrome/86.0.4240.198 Safari/537.36',
}
# 数据结构：
# 本来想之后统一存储的，但是还是选择爬一道题存一道题，因此一直没用到
# problem_list[ problem{pid : p_content[type, title, select[ {sid : s_content}, {sid : s_content}, ...], answer]}]
problem_list = []
problem = {}
p_content = []
select = []
cookies = {
	'Cookie': '对应链接的cookie，自己F12查看'
}


def init_write():
	with open('大数据学习通题库.md', 'w', encoding='utf-8') as file:
		pass


def write_line(content):
	with open('大数据学习通题库.md', 'a', encoding='utf-8') as file:
		file.write(content + '\n')


def get_chapter_problem(url):
	# 获取某个章节的题目和答案
	resp = requests.post(url=url, cookies=cookies, headers=headers)
	resp = resp.text

	# 输出爬取的网页源代码
	# print(resp)
	# return
	etree_html = etree.HTML(resp)
	# 题目
	xpath_all_problem = '//*[@class="mark_table padTop60 ans-cc"]/div'

	t = etree_html.xpath(xpath_all_problem)
	for i in t:
		# 遍历各个题型
		type = i.xpath('./h2[1]')[0].text
		print(type)
		if type.find('单选题') != -1:
			type = '单选题'
			write_line('## ' + type + '\n')
			# continue
			# 遍历单选题列表
			for problem_one_select in i.xpath('./div'):
				# 数据结构初始化
				problem = {}
				p_content = []
				select = []

				# 获取题目编号pid和题干title
				temp = problem_one_select.xpath('string(./h3)').split('.')
				pid = temp[0]
				title = temp[1]
				print('第', pid, '题', title)
				write_line(pid + '. ' + title + '\n')
				select_lis = problem_one_select.xpath('./ul[1]/li')
				# 遍历选项
				for li in select_lis:
					temp = li.xpath('string()').split('.')
					# 选项sid：A B C D
					sid = temp[0]
					# print(sid)

					# 选项对应的语句
					s_content = temp[1]
					print('选项', sid, '：', s_content)
					write_line(sid + ' ' + s_content + '\n')

					select.append({sid: s_content})
				# 获取答案
				answer = problem_one_select.xpath('./div[@class="mark_answer"]/div[@class="mark_key clearfix"]/span['
				                                  '@class="colorGreen marginRight40 fl"]/text()')[0]
				print('正确答案：', answer)
				write_line('\n正确答案：\n' + answer + '\n')

				# 装入数据结构
				p_content.append(type)
				p_content.append(title)
				p_content.append(select)
				p_content.append(answer)

				problem = {pid: p_content}
				problem_list.append(problem)

		# print(problem_list)
		elif type.find('多选题') != -1:
			# 逻辑和单选题一模一样
			type = '多选题'
			write_line('## ' + type + '\n')

			# continue
			# 遍历多选题列表
			for problem_multi_select in i.xpath('./div'):
				# 数据结构初始化
				problem = {}
				p_content = []
				select = []

				# 获取题目编号pid和题干title
				temp = problem_multi_select.xpath('string(./h3)').split('.')
				pid = temp[0]
				title = ''.join(temp[1:])
				print('第', pid, '题', title)
				write_line(pid + '. ' + title + '\n')

				select_lis = problem_multi_select.xpath('./ul[1]/li')
				# 遍历选项
				for li in select_lis:
					temp = li.xpath('string()').split('.')
					# 选项sid：A B C D
					sid = temp[0]
					# print(sid)

					# 选项对应的语句
					s_content = ''.join(temp[1:])
					print('选项', sid, '：', s_content)
					write_line(sid + ' ' + s_content + '\n')

					select.append({sid: s_content})
				# 获取答案
				answer = problem_multi_select.xpath('./div[@class="mark_answer"]/div[@class="mark_key clearfix"]/span['
				                                    '@class="colorGreen marginRight40 fl"]/text()')[0]
				print('正确答案：', answer)
				write_line('\n正确答案：\n' + answer + '\n')

				# 装入数据结构
				p_content.append(type)
				p_content.append(title)
				p_content.append(select)
				p_content.append(answer)

				problem = {pid: p_content}
				problem_list.append(problem)

		# print(problem_list)
		elif type.find('简答题') != -1:
			type = '简答题'
			write_line('## ' + type + '\n')

			# continue
			# 遍历简答题列表
			for problem_brief in i.xpath('./div'):
				# 数据结构初始化
				problem = {}
				p_content = []
				# 简答题此处为空
				select = []

				# 获取题目编号pid和题干title
				temp = problem_brief.xpath('string(./h3[1])').split('.')  # 有的地方的简答题题干爬取不到，如第10章的12和15题
				title = problem_brief.xpath('string(./p)')  # 虽然不知道为什么但是这样可以跑...
				pid = temp[0]
				score = temp[1].split(')')[0] + ')'
				# 应对题干爬取失效的情况
				title = temp[1].split(')')[1] == '' and title or temp[1].split(')')[1]
				print('第', pid, '题', score, title)
				write_line(pid + '. ' + score + title + '\n')

				# 获取答案，html标签也带上，因为有的答案是表格形式
				answer = problem_brief.xpath('./div[@class="mark_answer"]/div[@class="mark_answer_key pad0"]/dl['
				                             '@class="mark_fill colorGreen"]/dd[1]')[0]
				answer = etree.tostring(answer, encoding='unicode', pretty_print=True, method='html')  # 转为字符串

				# 使用正则表达式去除HTML标签的属性
				answer = re.sub(r'<(\w+)(\s+[^>]*)?>', r'<\1>', answer).replace('<span>', '') \
					.replace('</span>',
				             '').replace('<p>',
				                         '').replace(
					'</p>', '').replace('<dd>',
				                        '').replace(
					'</dd>', '').replace('\t', '').replace('\n\n', '').replace('<br/>', '').replace('<br>', '').strip()
				# 太多了，不输出
				# print('正确答案：', answer)
				write_line('\n正确答案：\n' + answer + '\n')

				# 装入数据结构
				p_content.append(type)
				p_content.append(title)
				p_content.append(select)
				p_content.append(answer)

				problem = {pid: p_content}
				problem_list.append(problem)

		# print(problem_list)
		elif type.find('填空题') != -1:
			type = '填空题'
			write_line('## ' + type + '\n')

			# continue
			# 遍历填空题列表
			for problem_blank in i.xpath('./div'):
				# 数据结构初始化
				problem = {}
				p_content = []
				# 简答题此处为空
				select = []

				# 获取题目编号pid和题干title
				temp = problem_blank.xpath('string(./h3[1])').split('.')
				pid = temp[0]
				title = ''.join(temp[1:])
				print('第', pid, '题', title)
				write_line(pid + '. ' + title + '\n')

				# 获取答案，html标签也带上，因为有的答案是表格形式
				answer = problem_blank.xpath('./div[@class="mark_answer"]/div[1]/dl['
				                             '@class="mark_fill colorGreen"]/dd/text()')
				answer = '\n'.join(answer)
				print('正确答案：', answer)
				write_line('\n正确答案：\n' + answer + '\n')

				# 装入数据结构
				p_content.append(type)
				p_content.append(title)
				p_content.append(select)
				p_content.append(answer)

				problem = {pid: p_content}
				problem_list.append(problem)

		# print(problem_list)
		else:
			print('未知的题型：', type)


if __name__ == '__main__':
	url = 'https://mooc1.chaoxing.com/mooc2/work/list?courseId=234766790&classId=77297858&cpi=156529108&ut=s&enc' \
	      '=27f8dfcdcda0b97e1d928bfc6e13fa57'
	resp = requests.get(url=url, cookies=cookies, headers=headers)
	resp = resp.text
	# print(resp)
	etree_html = etree.HTML(resp)

	# 获取章节列表
	chapter_xpath = '/html/body/div[2]/div/div/div[2]/div[2]/ul/li'
	chapters = etree_html.xpath(chapter_xpath)

	init_write()

	for chapter in chapters:
		chapter_url = chapter.xpath('./@data')[0]
		chapter_name = chapter.xpath('./@aria-label')[0]
		print(chapter_name, chapter_url)
		write_line('# [' + chapter_name + '](' + chapter_url + ')\n')
		get_chapter_problem(chapter_url)
	# break

# 将题库写入md中
