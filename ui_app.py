import customtkinter as ctk
from tkinter import messagebox
import threading
import queue
import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from task_star.core_logic import QuestionnaireFiller
from task_star.config import config, reload_global_config, ConfigLoader
from task_star.utils import setup_logger, logger
import yaml


class TaskHistory:
    """任务历史记录管理"""
    
    def __init__(self, history_file: str = None):
        if history_file is None:
            self.history_file = Path(__file__).parent / "logs" / "task_history.json"
        else:
            self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.records: List[Dict[str, Any]] = self._load()
    
    def _load(self) -> List[Dict[str, Any]]:
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def save(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.records[-100:], f, ensure_ascii=False, indent=2)
    
    def add(self, url: str, total: int, success: int, fail: int, duration: float):
        record = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'total': total,
            'success': success,
            'fail': fail,
            'duration': round(duration, 2)
        }
        self.records.append(record)
        self.save()
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.records[-limit:][::-1]


class TaskStarApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Task-Star 问卷自动填写助手 v3.0")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        self._task_running = False
        self._waiting_captcha = False
        self._task_start_time = None
        self.task_history = TaskHistory()
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self._create_menu()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_navigation()
        self._create_content_area()
        self._create_status_bar()
        
        self.filler_thread: Optional[threading.Thread] = None
        self.log_queue = queue.Queue()
        self.filler: Optional[QuestionnaireFiller] = None
        self._stop_event = threading.Event()
        
        self.show_home()
        
        self.after(100, self._update_log_display)
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _create_menu(self):
        """创建菜单栏"""
        try:
            self.menubar = ctk.CTkFrame(self, height=30)
            
            theme_label = ctk.CTkLabel(self.menubar, text="主题:", font=("", 12))
            theme_label.pack(side="left", padx=(10, 5))
            
            self.theme_menu = ctk.CTkOptionMenu(
                self.menubar, 
                values=["dark", "light", "system"],
                command=self._change_theme,
                width=80
            )
            self.theme_menu.set("dark")
            self.theme_menu.pack(side="left", padx=5)
            
            export_btn = ctk.CTkButton(
                self.menubar, 
                text="导出日志", 
                command=self._export_log,
                width=80,
                height=24,
                font=("", 11)
            )
            export_btn.pack(side="right", padx=10)
            
        except Exception:
            pass

    def _create_navigation(self):
        """创建导航栏"""
        self.nav_frame = ctk.CTkFrame(self, width=160, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nswe")
        self.nav_frame.grid_rowconfigure(5, weight=1)
        
        self.logo_label = ctk.CTkLabel(
            self.nav_frame, 
            text="⭐ Task-Star", 
            font=("", 20, "bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)
        
        nav_buttons = [
            ("🏠 首页", self.show_home, 1),
            ("🚀 开始任务", self.show_task, 2),
            ("⚙️ 设置", self.show_settings, 3),
            ("📊 历史记录", self.show_history, 4),
            ("❓ 帮助", self.show_help, 5),
        ]
        
        self.nav_buttons = {}
        for text, command, row in nav_buttons:
            btn = ctk.CTkButton(
                self.nav_frame, 
                text=text, 
                command=command,
                height=40,
                font=("", 14),
                fg_color="transparent",
                text_color=("gray10", "#DCE4EE"),
                hover_color=("gray70", "gray30"),
                anchor="w"
            )
            btn.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[text] = btn

    def _create_content_area(self):
        """创建主内容区域"""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        
        self.home_frame = self._create_home_frame()
        self.task_frame = self._create_task_frame()
        self.settings_frame = self._create_settings_frame()
        self.history_frame = self._create_history_frame()
        self.help_frame = self._create_help_frame()
        
        self.current_frame = None

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="we")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="就绪", 
            anchor="w",
            font=("", 12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        self.time_label = ctk.CTkLabel(
            self.status_frame, 
            text="", 
            anchor="e",
            font=("", 12)
        )
        self.time_label.pack(side="right", padx=10, pady=5)
        self._update_time()

    def _update_time(self):
        """更新时间显示"""
        self.time_label.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._update_time)

    def _create_home_frame(self) -> ctk.CTkFrame:
        """创建首页"""
        frame = ctk.CTkFrame(self.content_frame)
        
        title = ctk.CTkLabel(frame, text="欢迎使用 Task-Star", font=("", 28, "bold"))
        title.pack(pady=30)
        
        subtitle = ctk.CTkLabel(
            frame, 
            text="强大的问卷星自动填写工具", 
            font=("", 16),
            text_color="gray"
        )
        subtitle.pack()
        
        features_frame = ctk.CTkFrame(frame)
        features_frame.pack(pady=30, padx=50, fill="x")
        
        features = [
            ("✅", "支持单选、多选、填空、下拉选择题自动识别"),
            ("✅", "支持自定义答案池，随机选择答案"),
            ("✅", "验证码暂停机制，等待人工处理"),
            ("✅", "图形化配置，无需编写代码"),
            ("✅", "任务历史记录，方便查看统计"),
        ]
        
        for icon, text in features:
            row_frame = ctk.CTkFrame(features_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=5, padx=20)
            ctk.CTkLabel(row_frame, text=icon, font=("", 16)).pack(side="left")
            ctk.CTkLabel(row_frame, text=text, font=("", 14)).pack(side="left", padx=10)
        
        quick_start = ctk.CTkLabel(frame, text="快速开始", font=("", 18, "bold"))
        quick_start.pack(pady=(30, 10))
        
        steps = [
            "1. 点击左侧 \"⚙️ 设置\" 配置问卷链接和答案",
            "2. 点击左侧 \"🚀 开始任务\" 运行程序",
            "3. 观察日志输出，处理可能的验证码"
        ]
        
        for step in steps:
            ctk.CTkLabel(frame, text=step, font=("", 13)).pack(pady=3)
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        ctk.CTkButton(
            btn_frame, 
            text="立即配置", 
            command=self.show_settings,
            width=120,
            height=40,
            font=("", 14)
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="开始任务", 
            command=self.show_task,
            width=120,
            height=40,
            font=("", 14),
            fg_color="green",
            hover_color="darkgreen"
        ).pack(side="left", padx=10)
        
        return frame

    def _create_task_frame(self) -> ctk.CTkFrame:
        """创建任务页面"""
        frame = ctk.CTkFrame(self.content_frame)
        
        info_frame = ctk.CTkFrame(frame)
        info_frame.pack(fill="x", padx=10, pady=10)
        
        self.lbl_progress = ctk.CTkLabel(
            info_frame, 
            text="等待开始...", 
            font=("", 16, "bold")
        )
        self.lbl_progress.pack(pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(info_frame, width=500, height=20)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        
        self.stats_frame = ctk.CTkFrame(info_frame)
        self.stats_frame.pack(pady=10)
        
        self.lbl_success = ctk.CTkLabel(self.stats_frame, text="成功: 0", font=("", 14), text_color="green")
        self.lbl_success.pack(side="left", padx=20)
        
        self.lbl_fail = ctk.CTkLabel(self.stats_frame, text="失败: 0", font=("", 14), text_color="red")
        self.lbl_fail.pack(side="left", padx=20)
        
        self.lbl_duration = ctk.CTkLabel(self.stats_frame, text="耗时: 0秒", font=("", 14))
        self.lbl_duration.pack(side="left", padx=20)
        
        log_frame = ctk.CTkFrame(frame)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(log_frame, text="运行日志", font=("", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.text_log = ctk.CTkTextbox(log_frame, height=300, font=("", 12))
        self.text_log.pack(fill="both", expand=True, padx=10, pady=5)
        self.text_log.configure(state="disabled")
        
        control_frame = ctk.CTkFrame(frame, fg_color="transparent")
        control_frame.pack(pady=15)
        
        self.btn_run = ctk.CTkButton(
            control_frame, 
            text="▶ 开始运行", 
            command=self._start_task,
            width=120,
            height=40,
            font=("", 14),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_run.grid(row=0, column=0, padx=10)
        
        self.btn_stop = ctk.CTkButton(
            control_frame, 
            text="⏹ 停止", 
            command=self._stop_task,
            width=120,
            height=40,
            font=("", 14),
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.btn_stop.grid(row=0, column=1, padx=10)
        
        self.btn_continue = ctk.CTkButton(
            control_frame, 
            text="✓ 验证码已完成，继续", 
            command=self._resume_after_captcha,
            width=180,
            height=40,
            font=("", 14),
            fg_color="orange",
            hover_color="darkorange",
            state="disabled"
        )
        self.btn_continue.grid(row=0, column=2, padx=10)
        
        return frame

    def _create_settings_frame(self) -> ctk.CTkFrame:
        """创建设置页面"""
        frame = ctk.CTkFrame(self.content_frame)
        
        scroll = ctk.CTkScrollableFrame(frame)
        scroll.pack(fill="both", expand=True)
        
        ctk.CTkLabel(scroll, text="基础设置", font=("", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(10, 15), padx=10
        )
        
        settings_items = [
            ("问卷链接:", "entry_url", 400, "https://www.wjx.cn/jq/xxxx.aspx"),
            ("填写次数:", "entry_times", 100, "5"),
            ("提交间隔(秒):", "entry_interval", 100, "5"),
            ("重试次数:", "entry_retry", 100, "3"),
            ("页面超时(秒):", "entry_timeout", 100, "30"),
        ]
        
        self.settings_entries = {}
        for i, (label, key, width, placeholder) in enumerate(settings_items, start=1):
            ctk.CTkLabel(scroll, text=label, font=("", 13)).grid(
                row=i, column=0, sticky="w", padx=10, pady=8
            )
            entry = ctk.CTkEntry(scroll, width=width, placeholder_text=placeholder, font=("", 13))
            entry.grid(row=i, column=1, sticky="w", pady=8)
            self.settings_entries[key] = entry
        
        self.check_headless = ctk.CTkCheckBox(
            scroll, 
            text="后台运行 (无界面模式)", 
            font=("", 13)
        )
        self.check_headless.grid(row=6, column=0, columnspan=2, pady=8, padx=10, sticky="w")
        
        self.check_auto_submit = ctk.CTkCheckBox(
            scroll, 
            text="自动提交问卷", 
            font=("", 13)
        )
        self.check_auto_submit.grid(row=7, column=0, columnspan=2, pady=8, padx=10, sticky="w")
        self.check_auto_submit.select()
        
        ctk.CTkLabel(scroll, text="答题策略", font=("", 18, "bold")).grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(20, 15), padx=10
        )
        
        ctk.CTkLabel(scroll, text="多选题设置:", font=("", 13)).grid(
            row=9, column=0, sticky="w", padx=10, pady=8
        )
        
        multi_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        multi_frame.grid(row=9, column=1, sticky="w", pady=8)
        
        ctk.CTkLabel(multi_frame, text="最少选", font=("", 12)).pack(side="left")
        self.entry_min_sel = ctk.CTkEntry(multi_frame, width=50, placeholder_text="2", font=("", 12))
        self.entry_min_sel.pack(side="left", padx=5)
        ctk.CTkLabel(multi_frame, text="项，最多选", font=("", 12)).pack(side="left")
        self.entry_max_sel = ctk.CTkEntry(multi_frame, width=50, placeholder_text="3", font=("", 12))
        self.entry_max_sel.pack(side="left", padx=5)
        ctk.CTkLabel(multi_frame, text="项", font=("", 12)).pack(side="left")
        
        ctk.CTkLabel(
            scroll, 
            text="填空题答案池 (格式: 题号=答案1,答案2):", 
            font=("", 13)
        ).grid(row=10, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        self.text_blanks = ctk.CTkTextbox(scroll, height=120, width=550, font=("", 12))
        self.text_blanks.grid(row=11, column=0, columnspan=2, padx=10, pady=5)
        
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.grid(row=12, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(
            btn_frame, 
            text="💾 保存配置", 
            command=self._save_settings,
            width=120,
            height=35,
            font=("", 13)
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="🔄 重置默认", 
            command=self._reset_settings,
            width=120,
            height=35,
            font=("", 13),
            fg_color="gray",
            hover_color="darkgray"
        ).pack(side="left", padx=10)
        
        self._load_current_settings()
        
        return frame

    def _create_history_frame(self) -> ctk.CTkFrame:
        """创建历史记录页面"""
        frame = ctk.CTkFrame(self.content_frame)
        
        ctk.CTkLabel(frame, text="任务历史记录", font=("", 20, "bold")).pack(pady=20)
        
        columns_frame = ctk.CTkFrame(frame)
        columns_frame.pack(fill="x", padx=20, pady=10)
        
        columns = ["时间", "问卷链接", "总数", "成功", "失败", "耗时(秒)"]
        widths = [150, 300, 60, 60, 60, 80]
        
        for col, width in zip(columns, widths):
            ctk.CTkLabel(
                columns_frame, 
                text=col, 
                font=("", 13, "bold"),
                width=width
            ).pack(side="left", padx=5)
        
        self.history_list = ctk.CTkScrollableFrame(frame)
        self.history_list.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkButton(
            frame, 
            text="清除历史记录", 
            command=self._clear_history,
            width=120,
            height=35,
            font=("", 13),
            fg_color="red",
            hover_color="darkred"
        ).pack(pady=15)
        
        return frame

    def _create_help_frame(self) -> ctk.CTkFrame:
        """创建帮助页面"""
        frame = ctk.CTkFrame(self.content_frame)
        
        text_help = ctk.CTkTextbox(frame, font=("", 13))
        text_help.pack(fill="both", expand=True, padx=20, pady=20)
        
        help_content = """
# 使用帮助

## 1. 基础配置

### 问卷链接
- 必须是有效的问卷星链接 (wjx.cn)
- 格式示例: https://www.wjx.cn/jq/12345678.aspx

### 填写次数
- 建议 10-50 次为宜
- 过多可能触发风控机制

### 提交间隔
- 建议 3-10 秒
- 间隔过短容易被识别为机器

### 后台运行
- 勾选后浏览器将在后台运行，不显示窗口
- 适合服务器或批量任务

### 自动提交
- 勾选后自动点击提交按钮
- 取消勾选可用于调试，仅填写不提交

## 2. 答题策略详解

### 单选题
- 程序会自动识别并随机选择一个选项

### 多选题
- 可设置最少和最多选择的项数
- 例如：题目有5个选项，设置最少2，最多3
- 程序会随机选2个或3个选项

### 填空题
- 格式：题号=答案1,答案2,答案3
- 每行一个题号
- 程序会从列表中随机选一个填入
- 注意：题号是从1开始的实际题号

### 下拉选择题
- 程序会自动识别下拉框
- 随机选择一个非默认选项

## 3. 验证码处理

当检测到验证码时：
1. 程序会自动暂停
2. 日志显示"检测到验证码"提示
3. 在浏览器窗口中手动完成验证
4. 点击软件中的"验证码已完成，继续"按钮
5. 程序继续执行

## 4. 常见问题

### 为什么提交失败？
- 检查网络连接
- 尝试关闭"后台运行"模式，观察浏览器报错
- 检查问卷是否已关闭或达到填写上限

### 为什么题目没有填写？
- 检查 selectors.yaml 中的选择器是否正确
- 问卷星可能更新了页面结构

### ChromeDriver 版本不匹配？
- 运行: pip install --upgrade webdriver-manager
- 确保Chrome浏览器已更新到最新版本

## 5. 高级技巧

### 修改选择器
如果问卷星更新了页面导致程序失效，可以修改 config/selectors.yaml 文件中的CSS选择器。

### 代理设置
在配置文件中添加 proxy 项可以设置代理服务器。

### 日志导出
点击右上角"导出日志"按钮可以保存运行日志到文件。
        """
        text_help.insert("1.0", help_content)
        text_help.configure(state="disabled")
        
        return frame

    def _clear_content(self):
        """隐藏当前显示的页面"""
        if self.current_frame is not None:
            self.current_frame.pack_forget()
            self.current_frame = None

    def _show_frame(self, frame: ctk.CTkFrame):
        """显示指定页面"""
        self._clear_content()
        frame.pack(fill="both", expand=True)
        self.current_frame = frame

    def show_home(self):
        self._show_frame(self.home_frame)

    def show_task(self):
        self._show_frame(self.task_frame)

    def show_settings(self):
        self._show_frame(self.settings_frame)

    def show_history(self):
        self._show_frame(self.history_frame)
        self._refresh_history()

    def show_help(self):
        self._show_frame(self.help_frame)

    def _refresh_history(self):
        """刷新历史记录显示"""
        for widget in self.history_list.winfo_children():
            widget.destroy()
        
        records = self.task_history.get_recent(20)
        
        if not records:
            ctk.CTkLabel(
                self.history_list, 
                text="暂无历史记录", 
                font=("", 14),
                text_color="gray"
            ).pack(pady=20)
            return
        
        for record in records:
            row_frame = ctk.CTkFrame(self.history_list)
            row_frame.pack(fill="x", pady=3)
            
            data = [
                record.get('timestamp', '')[:19].replace('T', ' '),
                record.get('url', '')[:50] + ('...' if len(record.get('url', '')) > 50 else ''),
                str(record.get('total', 0)),
                str(record.get('success', 0)),
                str(record.get('fail', 0)),
                str(record.get('duration', 0))
            ]
            
            widths = [150, 300, 60, 60, 60, 80]
            for item, width in zip(data, widths):
                ctk.CTkLabel(
                    row_frame, 
                    text=item, 
                    font=("", 11),
                    width=width
                ).pack(side="left", padx=5)

    def _clear_history(self):
        """清除历史记录"""
        if messagebox.askyesno("确认", "确定要清除所有历史记录吗？"):
            self.task_history.records = []
            self.task_history.save()
            self._refresh_history()
            messagebox.showinfo("成功", "历史记录已清除")

    def _load_current_settings(self):
        """加载现有配置到界面"""
        if config is None:
            return
        
        try:
            self.settings_entries['entry_url'].insert(0, config.general.get('questionnaire_url', ''))
            self.settings_entries['entry_times'].insert(0, str(config.general.get('fill_times', 5)))
            self.settings_entries['entry_interval'].insert(0, str(config.general.get('interval_seconds', 5)))
            self.settings_entries['entry_retry'].insert(0, str(config.general.get('retry_count', 3)))
            self.settings_entries['entry_timeout'].insert(0, str(config.general.get('page_timeout', 30)))
            
            if config.general.get('headless'):
                self.check_headless.select()
            else:
                self.check_headless.deselect()
            
            if config.general.get('auto_submit', True):
                self.check_auto_submit.select()
            else:
                self.check_auto_submit.deselect()
            
            strat = config.strategy
            self.entry_min_sel.insert(0, str(strat.get('multi_choice', {}).get('min_select', 2)))
            self.entry_max_sel.insert(0, str(strat.get('multi_choice', {}).get('max_select', 3)))
            
            blanks = strat.get('fill_blanks', {})
            text = ""
            for k, v in blanks.items():
                if isinstance(v, list):
                    text += f"{k}={','.join(v)}\n"
                else:
                    text += f"{k}={v}\n"
            self.text_blanks.delete("1.0", "end")
            self.text_blanks.insert("1.0", text)
            
        except Exception as e:
            logger.error(f"加载配置失败: {e}")

    def _validate_settings(self) -> bool:
        """验证设置输入"""
        url = self.settings_entries['entry_url'].get().strip()
        if not url:
            messagebox.showerror("错误", "问卷链接不能为空")
            return False
        if not (url.startswith('http://') or url.startswith('https://')):
            messagebox.showerror("错误", "问卷链接格式不正确，必须以 http:// 或 https:// 开头")
            return False
        
        try:
            times = int(self.settings_entries['entry_times'].get())
            if times < 1:
                raise ValueError()
        except ValueError:
            messagebox.showerror("错误", "填写次数必须为正整数")
            return False
        
        try:
            interval = float(self.settings_entries['entry_interval'].get())
            if interval < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("错误", "提交间隔必须为非负数")
            return False
        
        try:
            min_sel = int(self.entry_min_sel.get())
            max_sel = int(self.entry_max_sel.get())
            if min_sel < 1 or max_sel < 1:
                raise ValueError()
            if min_sel > max_sel and max_sel != -1:
                messagebox.showerror("错误", "多选题最少选择数不能大于最多选择数")
                return False
        except ValueError:
            messagebox.showerror("错误", "多选题选择数必须为正整数")
            return False
        
        return True

    def _save_settings(self):
        """保存界面配置到文件"""
        if not self._validate_settings():
            return
        
        try:
            new_conf = {
                'general': {
                    'questionnaire_url': self.settings_entries['entry_url'].get().strip(),
                    'fill_times': int(self.settings_entries['entry_times'].get()),
                    'interval_seconds': float(self.settings_entries['entry_interval'].get()),
                    'retry_count': int(self.settings_entries['entry_retry'].get() or 3),
                    'page_timeout': int(self.settings_entries['entry_timeout'].get() or 30),
                    'headless': self.check_headless.get() == 1,
                    'auto_submit': self.check_auto_submit.get() == 1
                },
                'strategy': {
                    'single_choice': 'random',
                    'multi_choice': {
                        'min_select': int(self.entry_min_sel.get()),
                        'max_select': int(self.entry_max_sel.get())
                    },
                    'fill_blanks': self._parse_blanks()
                }
            }
            
            conf_path = Path(__file__).parent / "config" / "config.yaml"
            conf_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(conf_path, 'w', encoding='utf-8') as f:
                yaml.dump(new_conf, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
            reload_global_config()
            
            messagebox.showinfo("成功", "配置已保存！")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {e}")

    def _reset_settings(self):
        """重置为默认设置"""
        if messagebox.askyesno("确认", "确定要重置为默认设置吗？"):
            self.settings_entries['entry_url'].delete(0, "end")
            self.settings_entries['entry_url'].insert(0, "https://www.wjx.cn/jq/12345678.aspx")
            self.settings_entries['entry_times'].delete(0, "end")
            self.settings_entries['entry_times'].insert(0, "5")
            self.settings_entries['entry_interval'].delete(0, "end")
            self.settings_entries['entry_interval'].insert(0, "5")
            self.settings_entries['entry_retry'].delete(0, "end")
            self.settings_entries['entry_retry'].insert(0, "3")
            self.settings_entries['entry_timeout'].delete(0, "end")
            self.settings_entries['entry_timeout'].insert(0, "30")
            self.check_headless.deselect()
            self.check_auto_submit.select()
            self.entry_min_sel.delete(0, "end")
            self.entry_min_sel.insert(0, "2")
            self.entry_max_sel.delete(0, "end")
            self.entry_max_sel.insert(0, "3")
            self.text_blanks.delete("1.0", "end")
            self.text_blanks.insert("1.0", "1=张三,李四\n2=计算机学院,艺术学院")

    def _parse_blanks(self) -> Dict[int, List[str]]:
        """解析填空题输入"""
        text = self.text_blanks.get("1.0", "end").strip()
        res = {}
        for line in text.split('\n'):
            line = line.strip()
            if '=' in line:
                parts = line.split('=', 1)
                try:
                    k = int(parts[0].strip())
                    v = [x.strip() for x in parts[1].split(',')]
                    res[k] = v
                except ValueError:
                    continue
        return res

    def _start_task(self):
        """启动任务"""
        if self._task_running:
            return
        
        if config is None:
            messagebox.showerror("错误", "配置未加载，请先保存设置")
            return
        
        self._task_running = True
        self._waiting_captcha = False
        self._task_start_time = datetime.now()
        
        self.btn_run.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.btn_continue.configure(state="disabled")
        self.progress_bar.set(0)
        
        self.text_log.configure(state="normal")
        self.text_log.delete("1.0", "end")
        self.text_log.configure(state="disabled")
        
        self._stop_event = threading.Event()
        
        self.filler = QuestionnaireFiller(
            status_callback=self._update_status,
            log_callback=self._update_log_queue,
            progress_callback=self._update_progress,
            stop_event=self._stop_event
        )
        
        self.filler_thread = threading.Thread(target=self._run_task, daemon=True)
        self.filler_thread.start()
        
        self.show_task()
        self._update_duration()

    def _run_task(self):
        """在独立线程中运行任务"""
        try:
            self.filler.run()
        finally:
            self._task_running = False
            self.after(0, self._task_finished)

    def _task_finished(self):
        """任务完成后的处理"""
        self.btn_run.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.btn_continue.configure(state="disabled")
        
        if self.filler and self._task_start_time:
            duration = (datetime.now() - self._task_start_time).total_seconds()
            stats = self.filler.statistics
            
            if config:
                self.task_history.add(
                    url=config.general.get('questionnaire_url', ''),
                    total=stats['total'],
                    success=stats['success'],
                    fail=stats['fail'],
                    duration=duration
                )
            
            if stats['success'] > 0:
                messagebox.showinfo(
                    "任务完成", 
                    f"任务已完成！\n\n成功: {stats['success']} 份\n失败: {stats['fail']} 份\n耗时: {duration:.1f} 秒"
                )

    def _stop_task(self):
        """停止任务"""
        if self.filler:
            self.filler.stop()
        self._stop_event.set()
        self._update_status("正在停止...")

    def _resume_after_captcha(self):
        """验证码处理后继续"""
        if self.filler:
            self.filler.resume_after_captcha()
        self._waiting_captcha = False
        self.btn_continue.configure(state="disabled")

    def _update_status(self, msg: str):
        """更新状态栏"""
        self.after(0, lambda: self.status_label.configure(text=msg))

    def _update_log_queue(self, msg: str):
        """将日志放入队列"""
        self.log_queue.put(msg)

    def _update_progress(self, current: int, total: int):
        """更新进度条"""
        self.after(0, lambda: self._do_update_progress(current, total))

    def _do_update_progress(self, current: int, total: int):
        """执行进度更新"""
        if total > 0:
            self.progress_bar.set(current / total)
            self.lbl_progress.configure(text=f"正在处理: {current}/{total}")
        
        if self.filler:
            stats = self.filler.statistics
            self.lbl_success.configure(text=f"成功: {stats['success']}")
            self.lbl_fail.configure(text=f"失败: {stats['fail']}")

    def _update_duration(self):
        """更新耗时显示"""
        if self._task_running and self._task_start_time:
            duration = (datetime.now() - self._task_start_time).total_seconds()
            self.lbl_duration.configure(text=f"耗时: {int(duration)}秒")
            self.after(1000, self._update_duration)

    def _update_log_display(self):
        """定时从队列取出日志并显示"""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.text_log.configure(state="normal")
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.text_log.insert("end", f"[{timestamp}] {msg}\n")
                self.text_log.see("end")
                self.text_log.configure(state="disabled")
                
                if "验证码" in msg:
                    self._waiting_captcha = True
                    self.after(0, lambda: self.btn_continue.configure(state="normal"))
                    
        except queue.Empty:
            pass
        
        self.after(100, self._update_log_display)

    def _change_theme(self, theme: str):
        """切换主题"""
        ctk.set_appearance_mode(theme)

    def _export_log(self):
        """导出日志"""
        log_content = self.text_log.get("1.0", "end")
        if not log_content.strip():
            messagebox.showinfo("提示", "暂无日志可导出")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"taskstar_log_{timestamp}.txt"
        
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / default_name
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(log_content)
            messagebox.showinfo("成功", f"日志已导出到:\n{log_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {e}")

    def _on_closing(self):
        """窗口关闭处理"""
        if self._task_running:
            if messagebox.askyesno("确认", "任务正在运行，确定要退出吗？"):
                self._stop_task()
                if self.filler_thread and self.filler_thread.is_alive():
                    self.filler_thread.join(timeout=3)
                self.destroy()
        else:
            self.destroy()


if __name__ == "__main__":
    app = TaskStarApp()
    app.mainloop()
