from tkinter import Tk, Label, Listbox, Scrollbar, Button
from tkinter.filedialog import askopenfilenames, asksaveasfilename
from PyPDF2 import PdfMerger

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF合并工具")

        # 创建PDF文件合并器
        self.merger = PdfMerger()

        # 创建文件列表框和滚动条
        self.listbox = Listbox(self.root, width=50, height=10)
        self.scrollbar = Scrollbar(self.root, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 创建添加文件按钮
        self.add_button = Button(self.root, text="添加文件", command=self.add_files)
        self.add_button.pack(pady=10)

        # 创建合并按钮
        self.merge_button = Button(self.root, text="合并PDF", command=self.merge_pdf)
        self.merge_button.pack(pady=10)

    def add_files(self):
        # 使用对话框选择要添加的PDF文件
        file_paths = askopenfilenames(title='选择要添加的PDF文件', filetypes=[('PDF文件', '*.pdf')])

        # 将选择的文件路径添加到文件列表框中
        for file_path in file_paths:
            self.listbox.insert("end", file_path)

    def merge_pdf(self):
        # 清空合并器
        self.merger = PdfMerger()

        # 获取所有文件路径
        file_paths = self.listbox.get(0, "end")

        # 按照选择的先后顺序合并PDF文件
        for file_path in file_paths:
            self.merger.append(file_path)

        # 使用对话框选择导出的PDF文件路径和名称
        output_filepath = asksaveasfilename(title='选择导出的PDF文件', filetypes=[('PDF文件', '*.pdf')])

        # 如果用户选择了导出文件路径，则保存合并后的PDF文件
        if output_filepath:
            with open(output_filepath, 'wb') as output_file:
                self.merger.write(output_file)
            print('PDF文件合并完成！')

    def run(self):
        self.root.mainloop()

# 创建Tkinter根窗口
root = Tk()

# 禁止改变窗口大小
root.resizable(False, False)

# 创建PDF合并应用程序
app = PDFMergerApp(root)

# 运行应用程序
app.run()
