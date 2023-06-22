from tkinter import Tk
from tkinter.filedialog import askopenfilename
from PIL import Image

def convert_image_format(file_path, output_format):
    image = Image.open(file_path)

    # 如果图像是RGBA模式，将其转换为RGB模式
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    output_path = file_path[:file_path.rfind('.')] + '.' + output_format
    image.save(output_path)

def main():
    # 弹出选择文件窗口
    Tk().withdraw()
    file_path = askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if not file_path:
        print("未选择文件")
        return

    # 选择输出格式
    output_format = input("请输入要转换的格式（jpg/png）：")
    if output_format.lower() not in ['jpg', 'png']:
        print("无效的输出格式")
        return

    # 进行格式转换
    convert_image_format(file_path, output_format)

    print("图片转换完成！")

if __name__ == "__main__":
    main()
