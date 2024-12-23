import tkinter as tk
from tkinter import ttk, messagebox
import logging

class WindowManager:
    def __init__(self, parent, client):
        self.client = client
        self.window = tk.Toplevel(parent)
        self.window.title("窗口管理")
        self.window.geometry("600x400")

        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        columns = ("窗口标题", "窗口句柄")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor=tk.CENTER)

        # 刷新按钮
        refresh_button = tk.Button(self.window, text="刷新", command=self.refresh)
        refresh_button.pack(side=tk.LEFT, pady=10, padx=10)

        # 关闭按钮
        close_button = tk.Button(self.window, text="关闭窗口", command=self.close_window)
        close_button.pack(side=tk.RIGHT, pady=10, padx=10)

    def refresh(self):
        # 清空当前列表
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 获取窗口列表
        try:
            windows = self.get_windows()
            for window in windows:
                self.tree.insert("", tk.END, values=window)
        except Exception as e:
            logging.error(f"Failed to refresh window list: {e}")
            messagebox.showerror("错误", f"刷新窗口列表失败: {e}")

    def get_windows(self):
        # 模拟从远程客户端获取窗口列表
        # 实际上应该通过 self.client 与远程客户端通信获取数据
        return [("示例窗口1", "12345"), ("示例窗口2", "67890")]

    def close_window(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择一个窗口")
            return

        window_handle = self.tree.item(selected_item[0], "values")[1]
        try:
            self.send_close_command(window_handle)
            self.refresh()
        except Exception as e:
            logging.error(f"Failed to close window: {e}")
            messagebox.showerror("错误", f"关闭窗口失败: {e}")

    def send_close_command(self, window_handle):
        # 模拟发送关闭窗口命令到远程客户端
        # 实际上应该通过 self.client 与远程客户端通信发送命令
        logging.info(f"Closing window with handle: {window_handle}")
        # 这里添加实际的关闭窗口逻辑
