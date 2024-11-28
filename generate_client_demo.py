from tkinter import messagebox, Toplevel
import tkinter as tk

class generate_client():
    def __init__(self, master):
        self.master = master
        self.create_popup()
    
    def create_popup(self):
        # 创建弹窗
        dialog = Toplevel(self.master)
        dialog.title("生成服务端")
        dialog.geometry("300x120")
        dialog.resizable(False, False)

        # IP 输入框
        tk.Label(dialog, text="IP:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.E)
        ip_entry = tk.Entry(dialog)
        ip_entry.grid(row=0, column=1, padx=10, pady=10)

        # Port 输入框
        tk.Label(dialog, text="Port:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)
        port_entry = tk.Entry(dialog)
        port_entry.insert(0, "4444")  # 默认值
        port_entry.grid(row=1, column=1, padx=10, pady=10)

        # 确定按钮
        confirm_button = tk.Button(dialog, text="确定", command=lambda: self.generate_client_file(ip_entry, port_entry, dialog))
        confirm_button.grid(row=2, column=1, pady=10, sticky=tk.E)

    def generate_client_file( ip_entry, port_entry, dialog):
        ip = ip_entry.get().strip()
        port = port_entry.get().strip()

        if not ip or not port:
            messagebox.showerror("错误", "IP 和 Port 不能为空！")
            return

        # 模拟生成客户端文件
        file_name = "client_generated.py"
        try:
            with open(file_name, "w") as file:
                file.write(f"# Client configuration\nIP = '{ip}'\nPORT = {port}\n")
            messagebox.showinfo("成功", f"客户端文件已生成：{file_name}")
        except Exception as e:
            messagebox.showerror("错误", f"生成客户端文件失败：{e}")
        
        dialog.destroy()
