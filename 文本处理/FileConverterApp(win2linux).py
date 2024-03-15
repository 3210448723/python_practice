import tkinter as tk
from tkinter import filedialog, messagebox
import os

class FileConverterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("文件格式转换工具")

        self.source_path_label = tk.Label(master, text="源文件路径:")
        self.source_path_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

        self.source_path_var = tk.StringVar()
        self.source_path_entry = tk.Entry(master, textvariable=self.source_path_var, width=40)
        self.source_path_entry.grid(row=0, column=1, padx=10, pady=5)

        self.browse_button = tk.Button(master, text="浏览", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        self.convert_button = tk.Button(master, text="转换", command=self.convert_file)
        self.convert_button.grid(row=1, column=1, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="选择文件", filetypes=[("文件", "*.*")])
        if file_path:
            self.source_path_var.set(file_path)

    def convert_file(self):
        source_path = self.source_path_var.get()

        if not source_path:
            messagebox.showerror("错误", "请选择源文件")
            return

        output_path = filedialog.asksaveasfilename(title="选择输出路径和文件名", filetypes=[("文件", "*.*")])

        if not output_path:
            return  # 用户取消选择

        try:
            with open(source_path, 'r', encoding='UTF-8', newline='') as source_file:
                content = source_file.read()

            # 在这里添加换行符转换逻辑，例如将"\r\n"转换为"\n"或反之
            content = content.replace("\r\n", "\n")  # 示例：将Windows格式转换为Linux格式

            with open(output_path, 'w', encoding='UTF-8', newline='') as output_file:
                output_file.write(content)

            messagebox.showinfo("成功", "文件转换成功！")
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileConverterApp(root)
    root.mainloop()