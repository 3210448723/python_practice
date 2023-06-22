import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os

# 打开文件对话框，选择要处理的图片文件
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()

# 打开图片
image = Image.open(file_path)

# 获取原始图片的尺寸
original_width, original_height = image.size
original_size = os.path.getsize(file_path)  # 获取原始图片文件大小

# 获取用户输入的目标像素大小
target_pixel = input("请输入目标像素大小（格式：宽*高）：")
target_width, target_height = map(int, target_pixel.split('*'))

# 计算调整后的尺寸，保持纵横比例
if original_width > original_height:
    # 宽度较大，以宽度为基准调整高度
    adjusted_width = target_width
    adjusted_height = int(original_height * (target_width / original_width))
else:
    # 高度较大或相等，以高度为基准调整宽度
    adjusted_height = target_height
    adjusted_width = int(original_width * (target_height / original_height))

# 缩小图片像素
resized_image = image.resize((adjusted_width, adjusted_height), Image.ANTIALIAS)

# 显示估计的处理后文件大小
estimated_size = original_size * (adjusted_width * adjusted_height) / (original_width * original_height)
print("处理后的文件大小估计为：{:.2f} KB".format(estimated_size / 1024))

# 确认用户是否同意进行处理
confirmation = input("是否继续处理？（输入'yes'继续，其他任意键取消）：")

if confirmation.lower() == 'yes':
    # 保存处理后的图片
    save_path = filedialog.asksaveasfilename(filetypes=(("JPEG 文件", "*.jpg"), ("PNG 文件", "*.png"), ("所有文件", "*.*")))
    resized_image.save(save_path)

    print("处理完成！")
else:
    print("处理已取消！")
