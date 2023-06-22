from tkinter import Tk, filedialog, messagebox
import os
from pydub import AudioSegment

AudioSegment.converter = r"D:\Program Files\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffmpeg = r"D:\Program Files\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"D:\Program Files\ffmpeg\bin\ffprobe.exe"

# 创建一个Tkinter窗口
root = Tk()
root.withdraw()

# 定义支持的音频文件后缀名列表
supported_extensions = [
	("音频文件", "*.mp3;*.wav;*.m4a;*.ogg;*.flac;*.aac"),
]

# 选择要转换的音频文件
input_file_path = filedialog.askopenfilename(
	title="选择要转换的音频文件",
	filetypes=supported_extensions,
)

# 检查用户是否选择了文件
if not input_file_path:
	messagebox.showerror("错误", "未选择音频文件")
	exit()

# 定义支持的导出音频文件后缀名列表
export_extensions = [
	("MP3 文件", "*.mp3"),
	("WAV 文件", "*.wav"),
	("M4A 文件", "*.m4a"),
	("OGG 文件", "*.ogg"),
	("FLAC 文件", "*.flac"),
	("AAC 文件", "*.aac"),
]

# 选择导出音频的位置
output_file_path = filedialog.asksaveasfilename(
	title="选择导出音频的位置",
	defaultextension=".m4a",
	filetypes=export_extensions,
)

# 检查用户是否选择了导出位置
if not output_file_path:
	messagebox.showerror("错误", "未选择导出位置")
	exit()

# 获取输入文件的后缀名
input_extension = os.path.splitext(input_file_path)[1].lower()

# 获取输出文件的后缀名
output_extension = os.path.splitext(output_file_path)[1].lower()

try:
	# 使用pydub库加载音频文件
	audio = AudioSegment.from_file(input_file_path, format=input_extension[1:])

	# 导出音频文件
	audio.export(output_file_path, format=output_extension[1:])

	messagebox.showinfo("成功", "音频格式转换完成")
except Exception as e:
	messagebox.showerror("错误", str(e))
