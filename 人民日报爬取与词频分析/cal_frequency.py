import datetime

import jieba.analyse
import pdfplumber

from 人民日报爬取与词频分析 import save_results


def cal_words_frequency(path, time):
	time = str(time).replace("/", "").replace("-", "")

	text = ""
	with pdfplumber.open(
			path + time + ".pdf") as pdf:  # 每次循环打开一个pdf
		for i in range(len(pdf.pages)):
			firs = pdf.pages[i]  # 打开第一页（因每个pdf都是证书，只有一页）
			text += firs.extract_text()  # 读取第一页内容

	text = text.replace(" ", "")
	# 关键词抽取，topK为返回几个TF/IDF权重最大的关键词，allowPOS仅包括指定词性的词：'ns'地名、'n'普通名词、'vn'名动词、'v'普通动词
	words_list = jieba.analyse.extract_tags(text, topK=50, allowPOS=('ns', 'n'), withWeight=True)

	# 使用一个字典来统计每个关键词的出现次数和总的 TF-IDF 值
	keywords_freq = {}
	for i in words_list:
		# 这里的 round(tfidf, 2) 可以保留 TF-IDF 值的两位小数
		if '广告' != i[0]:
			keywords_freq[i[0]] = {"count": text.count(i[0]), "tfidf": i[1]}

	return keywords_freq


def convert_date(date_str):
	return '-'.join(str(date_str).split("/"))


if __name__ == '__main__':
	# 默认当天
	day = datetime.date.today()
	keywords_freq = cal_words_frequency("./newspaper/People's.Daily.", day)

	# 存储成文件
	day = convert_date(day)
	filename = save_results.save_to_csv(keywords_freq, day)
	# send_result.send_results(filename)
