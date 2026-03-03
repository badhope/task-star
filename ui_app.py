import customtkinter as ctk
from tkinter import messagebox
import threading
import queue
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径，以便正确导入
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from task_star.core_logic import QuestionnaireFiller
from task_star.config import config, ConfigLoader
import yaml

class TaskStarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Task-Star 问卷自动填写助手 v2.0")
        self.geometry("800x600")
        
        # 设置网格权重
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 创建导航栏
        self.nav_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nswe")
        self.nav_frame.grid_rowconfigure(4, weight=1) # 底部留白
        
        # 导航按钮
        self.btn_home = ctk.CTkButton(self.nav_frame, text="🏠 首页", command=self.show_home)
        self.btn_home.grid(row=0, column=0, padx=20, pady=20)
        
        self.btn_task = ctk.CTkButton(self.nav_frame, text="🚀 开始任务", command=self.show_task)
        self.btn_task.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_settings = ctk.CTkButton(self.nav_frame, text="⚙️ 设置", command=self.show_settings)
        self.btn_settings.grid(row=2, column=0, padx=20, pady=10)
        
        self.btn_help = ctk.CTkButton(self.nav_frame, text="❓ 帮助", command=self.show_help)
        self.btn_help.grid(row=3, column=0, padx=20, pady=10)
        
        # 主内容区域 (使用 Frame 切换)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        
        # 初始化各个页面（先不显示）
        self.home_frame = self.create_home_frame()
        self.task_frame = self.create_task_frame()
        self.settings_frame = self.create_settings_frame()
        self.help_frame = self.create_help_frame()
        
        # 当前显示的页面
        self.current_frame = None
        
        # 状态栏
        self.status_label = ctk.CTkLabel(self, text="就绪", anchor="w")
        self.status_label.grid(row=1, column=0, columnspan=2, sticky="we", padx=10)
        
        # 核心逻辑线程
        self.filler_thread = None
        self.log_queue = queue.Queue() # 用于线程间通信
        
        # 默认显示首页
        self.show_home()
        
        # 定时更新日志
        self.after(100, self.update_log_display)

    def clear_content(self):
        """隐藏当前显示的页面，而不是销毁"""
        if self.current_frame is not None:
            # 使用 pack_forget 隐藏而不是销毁
            self.current_frame.pack_forget()
            self.current_frame = None

    # --- 页面创建函数 ---
    
    def create_home_frame(self):
        frame = ctk.CTkFrame(self.content_frame)
        
        # 标题
        label_title = ctk.CTkLabel(frame, text="欢迎使用 Task-Star", font=("", 24, "bold"))
        label_title.pack(pady=30)
        
        # 介绍文字
        intro_text = """
        这是一个强大的问卷星自动填写工具。
        
        特性：
        ✅ 支持单选、多选、填空题自动识别
        ✅ 支持自定义答案池
        ✅ 支持验证码暂停机制
        ✅ 图形化配置，无需编写代码
        
        快速开始：
        1. 点击左侧 "⚙️ 设置" 配置问卷链接和答案。
        2. 点击左侧 "🚀 开始任务" 运行程序。
        3. 观察日志输出，处理可能的验证码。
        """
        label_intro = ctk.CTkLabel(frame, text=intro_text, justify="left", font=("", 14))
        label_intro.pack(padx=20, pady=10)
        
        # 快速入口按钮
        btn_start = ctk.CTkButton(frame, text="立即开始配置", height=40, command=self.show_settings)
        btn_start.pack(pady=20)
        
        # 初始时不 pack，由 show_home() 管理
        return frame

    def create_task_frame(self):
        frame = ctk.CTkFrame(self.content_frame)
        
        # 进度信息
        self.lbl_progress = ctk.CTkLabel(frame, text="等待开始...", font=("", 16))
        self.lbl_progress.pack(pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(frame, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        
        # 日志显示区
        self.text_log = ctk.CTkTextbox(frame, height=300)
        self.text_log.pack(fill="both", expand=True, padx=10, pady=10)
        self.text_log.configure(state="disabled") # 只读
        
        # 控制按钮
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        self.btn_run = ctk.CTkButton(btn_frame, text="▶ 开始运行", command=self.start_task, fg_color="green", hover_color="darkgreen")
        self.btn_run.grid(row=0, column=0, padx=10)
        
        self.btn_stop = ctk.CTkButton(btn_frame, text="⏹ 停止", command=self.stop_task, state="disabled", fg_color="red", hover_color="darkred")
        self.btn_stop.grid(row=0, column=1, padx=10)
        
        return frame

    def create_settings_frame(self):
        frame = ctk.CTkFrame(self.content_frame)
        
        # 使用 ScrollableFrame 以防内容过多
        scroll = ctk.CTkScrollableFrame(frame)
        scroll.pack(fill="both", expand=True)
        
        # --- 基础配置区 ---
        lbl_gen = ctk.CTkLabel(scroll, text="基础设置", font=("", 18, "bold"))
        lbl_gen.grid(row=0, column=0, columnspan=2, sticky="w", pady=10)
        
        # 链接
        ctk.CTkLabel(scroll, text="问卷链接:").grid(row=1, column=0, sticky="w", padx=10)
        self.entry_url = ctk.CTkEntry(scroll, width=400, placeholder_text="https://www.wjx.cn/jq/xxxx.aspx")
        self.entry_url.grid(row=1, column=1, pady=5)
        
        # 次数
        ctk.CTkLabel(scroll, text="填写次数:").grid(row=2, column=0, sticky="w", padx=10)
        self.entry_times = ctk.CTkEntry(scroll, width=100, placeholder_text="10")
        self.entry_times.grid(row=2, column=1, sticky="w", pady=5)
        
        # 提交间隔
        ctk.CTkLabel(scroll, text="提交间隔(秒):").grid(row=3, column=0, sticky="w", padx=10)
        self.entry_interval = ctk.CTkEntry(scroll, width=100, placeholder_text="3")
        self.entry_interval.grid(row=3, column=1, sticky="w", pady=5)
        
        # Headless 模式
        self.check_headless = ctk.CTkCheckBox(scroll, text="后台运行 (无界面模式，适合服务器)")
        self.check_headless.grid(row=4, column=0, columnspan=2, pady=5)
        
        # --- 策略配置区 ---
        lbl_strat = ctk.CTkLabel(scroll, text="答题策略", font=("", 18, "bold"))
        lbl_strat.grid(row=5, column=0, columnspan=2, sticky="w", pady=10)
        
        ctk.CTkLabel(scroll, text="多选题设置:").grid(row=6, column=0, sticky="w", padx=10)
        self.frame_multi = ctk.CTkFrame(scroll)
        self.frame_multi.grid(row=6, column=1, sticky="w", pady=5)
        ctk.CTkLabel(self.frame_multi, text="最少选").pack(side="left")
        self.entry_min_sel = ctk.CTkEntry(self.frame_multi, width=40, placeholder_text="2")
        self.entry_min_sel.pack(side="left", padx=5)
        ctk.CTkLabel(self.frame_multi, text="项，最多选").pack(side="left")
        self.entry_max_sel = ctk.CTkEntry(self.frame_multi, width=40, placeholder_text="3")
        self.entry_max_sel.pack(side="left", padx=5)
        ctk.CTkLabel(self.frame_multi, text="项").pack(side="left")
        
        # 填空题配置
        ctk.CTkLabel(scroll, text="填空题答案池 (格式: 题号=答案1,答案2):").grid(row=7, column=0, columnspan=2, sticky="w", padx=10, pady=(10,0))
        self.text_blanks = ctk.CTkTextbox(scroll, height=100, width=500)
        self.text_blanks.grid(row=8, column=0, columnspan=2, padx=10, pady=5)
        self.text_blanks.insert("1.0", "1=张三,李四\n2=计算机学院,艺术学院")
        
        # 保存按钮
        btn_save = ctk.CTkButton(scroll, text="💾 保存配置", command=self.save_settings)
        btn_save.grid(row=9, column=0, columnspan=2, pady=20)
        
        # 初始化加载当前配置
        self.load_current_settings()
        
        return frame

    def create_help_frame(self):
        frame = ctk.CTkFrame(self.content_frame)
        
        text_help = ctk.CTkTextbox(frame)
        text_help.pack(fill="both", expand=True, padx=10, pady=10)
        
        help_content = """
# 使用帮助

## 1. 基础配置
- **问卷链接**: 必须是有效的问卷星链接 (wjx.cn)。
- **填写次数**: 建议 10-50 次为宜，过多可能触发风控。

## 2. 答题策略详解
- **单选题**: 程序会自动识别并随机选择一个选项。
- **多选题**: 
  - 你可以设置最少和最多选择的项数。
  - 例如：题目有5个选项，设置最少2，最多3，程序会随机选2个或3个。
- **填空题**:
  - 格式：`题号=答案1,答案2,答案3`
  - 每行一个题号。
  - 程序会从逗号分隔的列表中随机选一个填入。
  - *注意：题号是从1开始的实际题号，不是页面上的顺序。*

## 3. 常见问题
- **遇到验证码怎么办？**
  程序会自动暂停并在日志中提示。请手动在浏览器中完成验证，然后点击软件中的“继续”按钮。
- **为什么提交失败？**
  检查网络连接，或者尝试关闭"后台运行"模式，观察浏览器是否有报错。

## 4. 高级技巧
- **修改 selectors.yaml**: 如果问卷星更新了页面导致程序失效，可以尝试更新 `config/selectors.yaml` 文件中的CSS选择器。
        """
        text_help.insert("1.0", help_content)
        text_help.configure(state="disabled")
        
        return frame

    # --- 功能逻辑 ---

    def show_home(self):
        self.clear_content()
        self.home_frame.pack(fill="both", expand=True)
        self.current_frame = self.home_frame

    def show_task(self):
        self.clear_content()
        self.task_frame.pack(fill="both", expand=True)
        self.current_frame = self.task_frame

    def show_settings(self):
        self.clear_content()
        self.settings_frame.pack(fill="both", expand=True)
        self.current_frame = self.settings_frame

    def show_help(self):
        self.clear_content()
        self.help_frame.pack(fill="both", expand=True)
        self.current_frame = self.help_frame

    def load_current_settings(self):
        """加载现有配置到界面"""
        if config:
            self.entry_url.insert(0, config.general.get('questionnaire_url', ''))
            self.entry_times.insert(0, str(config.general.get('fill_times', 1)))
            self.entry_interval.insert(0, str(config.general.get('interval_seconds', 3)))
            self.check_headless.select() if config.general.get('headless') else self.check_headless.deselect()
            
            strat = config.strategy
            self.entry_min_sel.insert(0, str(strat.get('multi_choice', {}).get('min_select', 2)))
            self.entry_max_sel.insert(0, str(strat.get('multi_choice', {}).get('max_select', 3)))
            
            # 加载填空题
            blanks = strat.get('fill_blanks', {})
            text = ""
            for k, v in blanks.items():
                text += f"{k}={','.join(v)}\n"
            self.text_blanks.delete("1.0", "end")
            self.text_blanks.insert("1.0", text)

    def save_settings(self):
        """保存界面配置到文件"""
        try:
            # 构建配置字典
            new_conf = {
                'general': {
                    'questionnaire_url': self.entry_url.get(),
                    'fill_times': int(self.entry_times.get()),
                    'interval_seconds': int(self.entry_interval.get()),
                    'headless': self.check_headless.get() == 1,
                    'auto_submit': True
                },
                'strategy': {
                    'multi_choice': {
                        'min_select': int(self.entry_min_sel.get()),
                        'max_select': int(self.entry_max_sel.get())
                    },
                    'fill_blanks': self._parse_blanks()
                }
            }
            
            # 写入文件
            conf_path = "config/config.yaml" # 需要处理相对路径
            with open(conf_path, 'w', encoding='utf-8') as f:
                yaml.dump(new_conf, f, allow_unicode=True, sort_keys=False)
                
            messagebox.showinfo("成功", "配置已保存！")
            # 重新加载全局配置
            ConfigLoader.reload() # 需要在ConfigLoader类中实现reload方法
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def _parse_blanks(self):
        """解析填空题输入"""
        text = self.text_blanks.get("1.0", "end").strip()
        res = {}
        for line in text.split('\n'):
            if '=' in line:
                k, v = line.split('=', 1)
                res[int(k.strip())] = [x.strip() for x in v.split(',')]
        return res

    def start_task(self):
        """
        启动问卷调查自动填写任务

        流程说明:
            1. 禁用运行按钮，启用停止按钮
            2. 重置日志显示区
            3. 创建停止事件对象
            4. 实例化核心逻辑并传入回调函数和停止事件
            5. 启动独立线程运行任务
            6. 自动切换到任务页面
        """
        self.btn_run.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.progress_bar.set(0)

        # 重置日志显示区
        self.text_log.configure(state="normal")
        self.text_log.delete("1.0", "end")
        self.text_log.configure(state="disabled")

        # 创建停止事件对象，用于从UI线程向工作线程发送停止信号
        self._stop_event = threading.Event()

        # 实例化核心逻辑，传入回调函数和停止事件
        self.filler = QuestionnaireFiller(
            status_callback=self.update_status,  # 状态更新回调
            log_callback=self.update_log_queue,  # 日志输出回调
            stop_event=self._stop_event  # 停止事件
        )

        # 启动独立线程运行任务，避免阻塞UI界面
        self.filler_thread = threading.Thread(target=self.filler.run, daemon=True)
        self.filler_thread.start()

        self.show_task()  # 自动跳转到任务页面

    def stop_task(self):
        """
        停止当前运行的任务

        流程说明:
            1. 设置停止事件标志，通知工作线程停止
            2. 更新状态栏显示
            3. 禁用停止按钮，启用运行按钮
        """
        if hasattr(self, '_stop_event'):
            self._stop_event.set()  # 设置停止标志
            self.update_status("正在停止...")
            # 等待线程结束
            if hasattr(self, 'filler_thread') and self.filler_thread.is_alive():
                self.filler_thread.join(timeout=5)  # 最多等待5秒
            # 恢复按钮状态
            self.btn_run.configure(state="normal")
            self.btn_stop.configure(state="disabled")

    def update_status(self, msg):
        self.status_label.configure(text=msg)

    def update_log_queue(self, msg):
        """将日志放入队列，实现线程安全通信"""
        self.log_queue.put(msg)

    def update_log_display(self):
        """定时从队列取出日志并显示"""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.text_log.configure(state="normal")
                self.text_log.insert("end", msg + "\n")
                self.text_log.see("end")
                self.text_log.configure(state="disabled")
        except queue.Empty:
            pass
        
        # 每100ms检查一次
        self.after(100, self.update_log_display)
