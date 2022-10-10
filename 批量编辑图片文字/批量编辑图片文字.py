# Author:Yuan Jinmin
# -*- coding = utf-8 -*-
# @Time  :2022/10/10 19:08
# @Author:YJM
# @Site  :
# @File  :批量编辑图片文字.py
# @Software: IntelliJ IDEA

from PIL import ImageFont, Image, ImageDraw
import csv

# 参数列表，例：张三,2001
list_path = "list.csv"
# 字体列表
font_path = r"C:\Windows\Fonts\simsun.ttc"
# 初始背景图片
imageFile = "test.jpg"
# 写入文字颜色
color = (255, 0, 0)

name = ''
college = '计算机科学与工程'
cls = '20计算机2班'
id = ''


def draw_bold_text(draw, xy, text, fill, font):
	draw.text((xy[0] - 1, xy[1]), text, fill, font)
	draw.text((xy[0] + 1, xy[1]), text, fill, font)
	draw.text((xy[0], xy[1] + 1), text, fill, font)
	draw.text((xy[0], xy[1] - 1), text, fill, font)


def write_text(id, name):
	# 设置字体，大小，宋体 常规，50 （如果没有，也可以不设置）
	font = ImageFont.truetype(font_path, 50)
	# font2 = ImageFont.truetype(r"C:\Windows\Fonts\simsun.ttc",60)
	# 要写入的文字
	text = name + "\n" \
	       + college + "\n" \
	       + cls + "\n" \
	       + id
	img = Image.open(imageFile)
	# 图片大小
	width, height = img.size
	# 计算出要写入的文字占用的像素
	w_t, h_t = font.getsize(text)

	# 在图片上添加文字
	draw = ImageDraw.Draw(img)
	draw_bold_text(draw=draw, xy=((width) / 2, (height - h_t) / 2), text=text, fill=color, font=font)
	# draw = ImageDraw.Draw(im1)
	# 保存
	img.save(name + id + ".png")


def read_csv(list_path):
	# 读取csv文件
	with open(list_path, "r", encoding="UTF-8") as f:
		reader = csv.reader(f)
		for row in reader:
			id = row[0]
			name = row[1]
			write_text(id, name)


if __name__ == '__main__':
	# 读入名单
	read_csv(list_path)