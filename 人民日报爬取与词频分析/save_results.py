import os
import csv

import os
import csv


def save_to_csv(keywords_freq, day):
	# 创建result文件夹
	if not os.path.exists('result'):
		os.mkdir('result')

	# 构造csv文件路径
	filename = f"result/{day}.csv"

	# 将keywords_freq保存到csv文件中
	with open(filename, 'w', newline='', encoding='GBK') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(['序号', '主题词', '当天报面出现次数', 'TF-IDF值'])
		for i, (keyword, freq) in enumerate(keywords_freq.items()):
			row = [i + 1, keyword, freq['count'], freq['tfidf']]
			writer.writerow(row)

	print(f"已将结果保存到{filename}")
	return filename


if __name__ == '__main__':
	# 示例用法
	keywords_freq = {'中国': {'count': 307, 'tfidf': 0.11341547241089336},
	                 '菌草': {'count': 51, 'tfidf': 0.07923909295870317}}
	day = "2000-04-14"
	save_to_csv(keywords_freq, day)
