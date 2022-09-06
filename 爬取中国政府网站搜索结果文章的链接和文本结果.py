import requests
from lxml import html

# 如果有报错可以参考该文章
# 我采用了第一种方法（修改了D:\Program Files\Python39\Lib\site-packages\urllib3\response.py 的697行 改成了elf.chunk_left = int(line, 16) if line else 0）
# https://blog.csdn.net/wangzuxi/article/details/40377467

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
}


def req(url, keyword, pageSize, currentPage, p):
	url = url + keyword + pageSize + currentPage + str(p)
	text = requests.get(url=url, headers=headers).text
	# print(text)
	tree = html.etree.HTML(text)
	# 题目编号
	ul = tree.xpath('//*[@class="result"]/ul/li')
	for item in ul:
		href = item.xpath('./h3/a/@href')[0]
		# 避免 相关图片和相关视频 干扰结果
		if href.find("s.htm?") != -1:
			continue
		print(href, sep=" ")

		# 防止乱码
		text = requests.get(href, headers)
		text.encoding = text.apparent_encoding  # 获取编码
		text = text.text

		item = html.etree.HTML(text)
		title = item.xpath('//div[@class="article oneColumn pub_border"]/h1/text()')[0].replace(" ", "")
		print(title, sep=" ")
		texts = item.xpath('//div[@id="UCAP-CONTENT"]/p')
		content = ''
		for text in texts:
			# 还可排除图片的干扰
			try:
				content += text.xpath('./span/text()')[0].replace(" ", "")
			except Exception:
				pass
			try:
				content += text.xpath('./text()')[0].replace(" ", "")
			except Exception:
				pass
		print(content)


if __name__ == "__main__":
	url = "http://sousuo.gov.cn/s.htm?t=govall&advance=false&n=&timetype=&mintime=&maxtime=&sort="
	# 关键字，可修改
	keyword = "&q=中欧班列"
	# 页面大小
	pageSize = "&n=10"
	currentPage = "&p="
	# 当前页码
	# 第一页
	p = 0
	req(url, keyword, pageSize, currentPage, p)
