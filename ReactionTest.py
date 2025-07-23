import tkinter as tk
import time
import random

class ReactionTimePressApp:
    def __init__(self, master):
        self.master = master
        master.title("反应时间测试 (按下)")
        master.geometry("400x300") # 设置窗口大小
        master.config(bg="light grey") # 默认背景色

        self.state = "idle" # idle, waiting, signal, result
        self.start_time = 0
        self.reaction_time = 0
        self.timer_id = None # 用于存储 .after() 的 ID

        # --- UI 元素 ---
        self.instructions_label = tk.Label(master, text="点击“开始”按钮，等待背景变绿后\n尽快点击鼠标左键",
                                           font=("Arial", 12), bg="light grey", justify="center")
        self.instructions_label.pack(pady=20)

        self.result_label = tk.Label(master, text="", font=("Arial", 18, "bold"), bg="light grey")
        self.result_label.pack(pady=30)

        self.start_button = tk.Button(master, text="开始测试", font=("Arial", 14), command=self.start_test)
        self.start_button.pack(pady=10)

        # --- 事件绑定 ---
        # 初始时不绑定点击事件，在状态变化时绑定/解绑
        self.click_binding_id = None # 用于存储 bind 返回的 ID，方便解绑

        master.focus_set() # 确保窗口能接收事件

    def start_test(self):
        # 防止在测试过程中重复点击开始
        if self.state != "idle" and self.state != "result":
            return

        self.state = "waiting"
        self.master.config(bg="orange") # 等待时背景变橙色
        self.instructions_label.config(text="准备... 等待绿色出现...", bg="orange")
        self.result_label.config(text="") # 清除上次结果
        self.start_button.pack_forget() # 隐藏开始按钮

        # 解绑可能存在的旧的点击事件
        self.unbind_click()

        # 绑定“过早点击”的检测
        self.click_binding_id = self.master.bind("<ButtonPress-1>", self.handle_false_start)

        # 清除可能存在的旧计时器
        if self.timer_id:
            self.master.after_cancel(self.timer_id)

        # 随机延迟 1.5 到 5 秒后触发信号
        delay_ms = random.randint(1500, 5000)
        self.timer_id = self.master.after(delay_ms, self.trigger_signal)

    def trigger_signal(self):
        # 必须在等待状态才能触发信号
        if self.state != "waiting":
            return

        self.state = "signal"
        self.master.config(bg="light green") # 信号：背景变绿
        self.instructions_label.config(text="点击鼠标左键！", bg="light green")

        # 解绑“过早点击”的检测
        self.unbind_click()
        # 绑定“反应点击”的检测
        self.click_binding_id = self.master.bind("<ButtonPress-1>", self.handle_reaction_click)

        self.start_time = time.perf_counter() # 信号出现时开始计时

    def handle_reaction_click(self, event):
        # 只有在信号发出后点击才有效
        if self.state != "signal":
            return

        end_time = time.perf_counter()
        self.reaction_time = (end_time - self.start_time) * 1000 # 转换为毫秒

        self.state = "result"
        self.master.config(bg="light grey") # 恢复默认背景
        self.instructions_label.config(text="测试完成！点击“开始”重试", bg="light grey")
        self.result_label.config(text=f"反应时间：{self.reaction_time:.2f} 毫秒")

        # 解绑点击事件
        self.unbind_click()
        # 重新显示开始按钮
        self.start_button.pack(pady=10)


    def handle_false_start(self, event):
        # 在等待信号时点击了
        if self.state != "waiting":
            return

        self.state = "result" # 或 "false_start" 状态
        # 取消计划中的信号触发
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

        self.master.config(bg="red") # 错误提示用红色
        self.instructions_label.config(text="太快了！点击太早。\n点击“开始”重试", bg="red", fg="white")
        self.result_label.config(text="")

        # 解绑点击事件
        self.unbind_click()
        # 重新显示开始按钮
        self.start_button.pack(pady=10)

    def unbind_click(self):
        """安全地解绑鼠标点击事件"""
        if self.click_binding_id:
            self.master.unbind("<ButtonPress-1>", self.click_binding_id)
            self.click_binding_id = None


# --- 主程序入口 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ReactionTimePressApp(root)
    root.mainloop()