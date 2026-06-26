#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片筛选浏览工具 v4.0
现代化设计风格，圆角UI，类似美图秀秀风格
"""

import os
import sys
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import ctypes

# 隐藏控制台窗口（Windows）
if sys.platform == 'win32':
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

try:
    from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFilter
except ImportError:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("错误", "需要安装 Pillow 库。\n请运行：pip install Pillow")
    sys.exit(1)


# 现代化配色方案
COLORS = {
    'bg_primary': '#FFFFFF',         # 主背景
    'bg_secondary': '#F7F8FA',       # 次背景
    'bg_card': '#FFFFFF',            # 卡片背景
    'bg_sidebar': '#FAFAFA',         # 侧边栏
    'bg_canvas': '#F0F2F5',          # 画布背景
    'accent': '#FF4757',             # 主色调（红色，类似美图）
    'accent_hover': '#FF6B7A',
    'accent_pressed': '#E63946',
    'text_primary': '#1F2329',       # 主文字
    'text_secondary': '#646A73',     # 次文字
    'text_tertiary': '#8F959E',      # 三级文字
    'border': '#E5E6EB',             # 边框
    'border_light': '#F2F3F5',       # 浅边框
    'success': '#00B42A',
    'warning': '#FF7D00',
    'shadow': '#00000010',
}


class ConfigManager:
    """配置管理器"""
    def __init__(self):
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(app_dir, "image_viewer_config.json")
        self.config = {
            "source_dir": "",
            "output_dir": "",
            "last_index": 0,
            "last_image_path": "",
            "zoom_level": 1.0
        }
        self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
        except Exception as e:
            print(f"加载配置失败: {e}")

    def save_config(self):
        try:
            config_dir = os.path.dirname(self.config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()


class RoundedButton(tk.Canvas):
    """圆角按钮 - 使用Canvas绘制"""
    def __init__(self, parent, text="", command=None, width=120, height=36,
                 bg=COLORS['accent'], hover_bg=None, pressed_bg=None,
                 text_color='white', font=('Microsoft YaHei UI', 10, 'bold'),
                 radius=8, icon=None, **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=parent.cget('bg') if 'bg' in parent.keys() else COLORS['bg_primary'],
                        highlightthickness=0, bd=0, **kwargs)
        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.bg = bg
        self.bg_normal = bg
        self.bg_hover = hover_bg or bg
        self.bg_pressed = pressed_bg or bg
        self.text_color = text_color
        self.font = font
        self.radius = radius
        self.icon = icon
        self.state = 'normal'
        self._draw(bg)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self, bg_color, text_color=None):
        self.delete("all")
        # 绘制圆角矩形
        r = self.radius
        w, h = self.width, self.height
        # 圆角矩形（用4个圆弧+2个矩形+1个矩形）
        self.create_arc((0, 0, r*2, r*2), start=90, extent=90, fill=bg_color, outline=bg_color)
        self.create_arc((w-r*2, 0, w, r*2), start=0, extent=90, fill=bg_color, outline=bg_color)
        self.create_arc((0, h-r*2, r*2, h), start=180, extent=90, fill=bg_color, outline=bg_color)
        self.create_arc((w-r*2, h-r*2, w, h), start=270, extent=90, fill=bg_color, outline=bg_color)
        self.create_rectangle((r, 0, w-r, h), fill=bg_color, outline=bg_color)
        self.create_rectangle((0, r, w, h-r), fill=bg_color, outline=bg_color)

        # 文字
        tc = text_color or self.text_color
        if self.icon and self.text:
            self.create_text(w/2 + 8, h/2, text=self.text, fill=tc, font=self.font, anchor='center')
        elif self.icon:
            self.create_text(w/2, h/2, text=self.icon, fill=tc, font=self.font, anchor='center')
        else:
            self.create_text(w/2, h/2, text=self.text, fill=tc, font=self.font, anchor='center')

    def _on_enter(self, e):
        if self.state == 'normal':
            self._draw(self.bg_hover)
            self.config(cursor='hand2')

    def _on_leave(self, e):
        if self.state == 'normal':
            self._draw(self.bg_normal)
            self.config(cursor='')

    def _on_press(self, e):
        self._draw(self.bg_pressed)

    def _on_release(self, e):
        if self.command:
            self.command()


class RoundedCard(tk.Canvas):
    """圆角卡片背景"""
    def __init__(self, parent, width=200, height=100, radius=10,
                 bg=COLORS['bg_card'], **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=parent.cget('bg') if 'bg' in parent.keys() else COLORS['bg_primary'],
                        highlightthickness=0, bd=0, **kwargs)
        self.w = width
        self.h = height
        self.r = radius
        self.bg = bg
        self._draw()

    def _draw(self, color=None):
        color = color or self.bg
        self.delete("all")
        r = self.r
        w, h = self.w, self.h
        self.create_arc((0, 0, r*2, r*2), start=90, extent=90, fill=color, outline=color)
        self.create_arc((w-r*2, 0, w, r*2), start=0, extent=90, fill=color, outline=color)
        self.create_arc((0, h-r*2, r*2, h), start=180, extent=90, fill=color, outline=color)
        self.create_arc((w-r*2, h-r*2, w, h), start=270, extent=90, fill=color, outline=color)
        self.create_rectangle((r, 0, w-r, h), fill=color, outline=color)
        self.create_rectangle((0, r, w, h-r), fill=color, outline=color)


class ImageViewer:
    def __init__(self, root):
        self.root = root
        self.config = ConfigManager()
        self.setup_window()

        # 变量
        self.current_dir = self.config.get("source_dir", "")
        self.output_dir = self.config.get("output_dir", "")
        self.image_files = []
        self.current_index = self.config.get("last_index", 0)
        self.current_image = None
        self.photo_image = None
        self.last_image_path = self.config.get("last_image_path", "")

        # 缩放
        self.zoom_level = self.config.get("zoom_level", 1.0)
        self.zoom_factor = 1.2
        self.min_zoom = 0.1
        self.max_zoom = 10.0

        # 拖动
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.image_x = 0
        self.image_y = 0
        self.is_dragging = False

        # 缓存原始图片（避免重复读取磁盘）
        self.cached_original = None
        self.cached_path = None

        self.create_widgets()
        self.bind_events()

        if self.current_dir and os.path.exists(self.current_dir):
            self.path_label.config(text=self.current_dir)
            self.load_images()
        else:
            self.config.set("source_dir", "")
            self.config.set("last_index", 0)
            self.config.set("last_image_path", "")
            self.update_status("请先选择图片文件夹")

    def setup_window(self):
        self.root.title("图片筛选工具 v4.0")

        # 获取屏幕尺寸，窗口占1/4屏幕并居中
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        ww = sw * 2 // 3
        wh = sh * 2 // 3
        x = (sw - ww) // 2
        y = (sh - wh) // 2
        self.root.geometry(f"{ww}x{wh}+{x}+{y}")

        self.root.minsize(600, 400)
        self.root.configure(bg=COLORS['bg_primary'])

        # 圆角窗口（Windows 11支持）
        try:
            from ctypes import windll, byref, c_int, sizeof, c_void_p
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            preference = c_int(2)  # DWMWCP_ROUND
            windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE,
                                                byref(preference), sizeof(preference))
        except:
            pass

        # 图标
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass

    def create_widgets(self):
        # ============ 主容器 ============
        main_container = tk.Frame(self.root, bg=COLORS['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # ============ 顶部导航栏（圆角卡片） ============
        nav_card = tk.Frame(main_container, bg=COLORS['bg_card'], highlightbackground=COLORS['border_light'],
                           highlightthickness=1, bd=0)
        nav_card.pack(fill=tk.X, pady=(0, 10), ipady=8)

        # 左侧：Logo + 标题
        left_nav = tk.Frame(nav_card, bg=COLORS['bg_card'])
        left_nav.pack(side=tk.LEFT, padx=15)

        # Logo占位
        logo_canvas = tk.Canvas(left_nav, width=28, height=28, bg=COLORS['bg_card'],
                              highlightthickness=0, bd=0)
        logo_canvas.pack(side=tk.LEFT, pady=8)
        # 绘制Logo（红色圆角矩形+白色方块）
        logo_canvas.create_rectangle((2, 4, 26, 24), fill=COLORS['accent'], outline='')
        logo_canvas.create_rectangle((8, 10, 20, 18), fill='white', outline='')
        logo_canvas.create_polygon((14, 10, 20, 14, 14, 18), fill=COLORS['accent'], outline='')

        title_label = tk.Label(left_nav, text="图片筛选工具", font=('Microsoft YaHei UI', 13, 'bold'),
                             fg=COLORS['text_primary'], bg=COLORS['bg_card'])
        title_label.pack(side=tk.LEFT, padx=(8, 0), pady=8)

        # 右侧：缩放控制 + 保存按钮
        right_nav = tk.Frame(nav_card, bg=COLORS['bg_card'])
        right_nav.pack(side=tk.RIGHT, padx=15, pady=4)

        # 重置缩放
        self.reset_nav_btn = RoundedButton(right_nav, text="重置", width=48, height=24,
                                           bg=COLORS['bg_secondary'],
                                           hover_bg=COLORS['border'],
                                           text_color=COLORS['text_primary'],
                                           font=('Microsoft YaHei UI', 8),
                                           radius=4,
                                           command=self.reset_zoom)
        self.reset_nav_btn.pack(side=tk.LEFT, padx=(0, 6))

        # 缩放控件
        self.zoom_out_small = tk.Label(right_nav, text="➖", font=('Microsoft YaHei UI', 11),
                                       fg=COLORS['text_secondary'], bg=COLORS['bg_card'],
                                       cursor='hand2', padx=4)
        self.zoom_out_small.pack(side=tk.LEFT)
        self.zoom_out_small.bind("<Button-1>", lambda e: self.zoom_out())

        self.zoom_label = tk.Label(right_nav, text="100%",
                                  font=('Microsoft YaHei UI', 10, 'bold'),
                                  fg=COLORS['text_primary'], bg=COLORS['bg_card'])
        self.zoom_label.pack(side=tk.LEFT, padx=4)

        self.zoom_in_small = tk.Label(right_nav, text="➕", font=('Microsoft YaHei UI', 11),
                                      fg=COLORS['text_secondary'], bg=COLORS['bg_card'],
                                      cursor='hand2', padx=4)
        self.zoom_in_small.pack(side=tk.LEFT)
        self.zoom_in_small.bind("<Button-1>", lambda e: self.zoom_in())

        # 分隔
        tk.Frame(right_nav, width=1, height=20, bg=COLORS['border']).pack(side=tk.LEFT, padx=8)

        # 保存按钮（圆角）
        self.save_nav_btn = RoundedButton(right_nav, text="保存", width=64, height=28,
                                          bg=COLORS['bg_secondary'],
                                          hover_bg=COLORS['border'],
                                          text_color=COLORS['text_primary'],
                                          font=('Microsoft YaHei UI', 10),
                                          radius=6,
                                          command=self.save_current_image)
        self.save_nav_btn.pack(side=tk.LEFT, padx=(0, 8))

        # ============ 中部区域（侧边栏 + 主画布） ============
        content_frame = tk.Frame(main_container, bg=COLORS['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True)

        # --- 左侧栏 ---
        self.sidebar = tk.Frame(content_frame, bg=COLORS['bg_secondary'],
                               width=220, highlightbackground=COLORS['border_light'],
                               highlightthickness=1, bd=0)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.sidebar.pack_propagate(False)

        # 侧边栏标题
        sidebar_title = tk.Label(self.sidebar, text="操作",
                                font=('Microsoft YaHei UI', 11, 'bold'),
                                fg=COLORS['text_secondary'], bg=COLORS['bg_secondary'])
        sidebar_title.pack(anchor='w', padx=20, pady=(20, 10))

        # 侧边栏按钮
        sidebar_items = [
            ("📂  打开文件夹", self.select_source_dir, True),
            ("📤  设置输出", self.select_output_dir, False),
        ]

        for text, cmd, is_active in sidebar_items:
            btn_frame = tk.Frame(self.sidebar, bg=COLORS['bg_secondary'], cursor='hand2')
            btn_frame.pack(fill=tk.X, padx=12, pady=2)

            if is_active:
                # 激活状态 - 红色左边框
                active_indicator = tk.Frame(btn_frame, bg=COLORS['accent'], width=3)
                active_indicator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

            item_label = tk.Label(btn_frame, text=text,
                                 font=('Microsoft YaHei UI', 10),
                                 fg=COLORS['accent'] if is_active else COLORS['text_primary'],
                                 bg=COLORS['bg_secondary'],
                                 anchor='w', padx=12, pady=10, cursor='hand2')
            item_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            if cmd:
                item_label.bind("<Button-1>", lambda e, c=cmd: c())
                btn_frame.bind("<Button-1>", lambda e, c=cmd: c())

        # 侧边栏底部信息
        info_label = tk.Label(self.sidebar, text="快捷键",
                             font=('Microsoft YaHei UI', 10, 'bold'),
                             fg=COLORS['text_secondary'], bg=COLORS['bg_secondary'])
        info_label.pack(anchor='w', padx=20, pady=(30, 8))

        shortcuts = [
            ("← →", "切换图片"),
            ("滚轮", "缩放图片"),
            ("拖动", "平移图片"),
            ("S", "保存图片"),
            ("ESC", "退出程序"),
        ]
        for key, desc in shortcuts:
            row = tk.Frame(self.sidebar, bg=COLORS['bg_secondary'])
            row.pack(fill=tk.X, padx=20, pady=1)
            tk.Label(row, text=key, font=('Microsoft YaHei UI', 9, 'bold'),
                    fg=COLORS['text_primary'], bg=COLORS['bg_secondary'], width=6, anchor='w').pack(side=tk.LEFT)
            tk.Label(row, text=desc, font=('Microsoft YaHei UI', 9),
                    fg=COLORS['text_tertiary'], bg=COLORS['bg_secondary']).pack(side=tk.LEFT)

        # 清空记录按钮
        clear_btn = RoundedButton(self.sidebar, text="🗑  清空记录",
                                  width=160, height=30,
                                  bg='#FFF0F0',
                                  hover_bg='#FFD6D6',
                                  text_color=COLORS['accent'],
                                  font=('Microsoft YaHei UI', 9),
                                  radius=6,
                                  command=self.clear_records)
        clear_btn.pack(side=tk.BOTTOM, padx=20, pady=20)

        # --- 右侧主画布区域 ---
        canvas_container = tk.Frame(content_frame, bg=COLORS['bg_card'],
                                   highlightbackground=COLORS['border_light'],
                                   highlightthickness=1, bd=0)
        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 顶部路径栏
        path_bar = tk.Frame(canvas_container, bg=COLORS['bg_card'])
        path_bar.pack(fill=tk.X, padx=15, pady=(10, 5))

        # 文件夹选择按钮（圆角）
        self.select_btn = RoundedButton(path_bar, text="📂  选择图片文件夹",
                                        width=140, height=30,
                                        bg=COLORS['accent'],
                                        hover_bg=COLORS['accent_hover'],
                                        pressed_bg=COLORS['accent_pressed'],
                                        text_color='white',
                                        font=('Microsoft YaHei UI', 9, 'bold'),
                                        radius=6,
                                        command=self.select_source_dir)
        self.select_btn.pack(side=tk.LEFT, padx=(0, 10))

        # 路径显示
        self.path_label = tk.Label(path_bar, text="未选择文件夹",
                                  font=('Microsoft YaHei UI', 9),
                                  fg=COLORS['text_tertiary'],
                                  bg=COLORS['bg_card'], anchor='w')
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 画布
        self.canvas = tk.Canvas(canvas_container, bg=COLORS['bg_canvas'],
                              highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 10))

        # 底部控制栏
        bottom_bar = tk.Frame(main_container, bg=COLORS['bg_primary'])
        bottom_bar.pack(fill=tk.X, pady=(10, 0))

        # 左侧：导航
        left_bottom = tk.Frame(bottom_bar, bg=COLORS['bg_primary'])
        left_bottom.pack(side=tk.LEFT)

        # 上一张/下一张按钮
        self.prev_btn = RoundedButton(left_bottom, text="◀  上一张",
                                      width=90, height=32,
                                      bg=COLORS['bg_card'],
                                      hover_bg=COLORS['bg_secondary'],
                                      text_color=COLORS['text_primary'],
                                      font=('Microsoft YaHei UI', 9),
                                      radius=6,
                                      command=self.prev_image)
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.next_btn = RoundedButton(left_bottom, text="下一张  ▶",
                                      width=90, height=32,
                                      bg=COLORS['bg_card'],
                                      hover_bg=COLORS['bg_secondary'],
                                      text_color=COLORS['text_primary'],
                                      font=('Microsoft YaHei UI', 9),
                                      radius=6,
                                      command=self.next_image)
        self.next_btn.pack(side=tk.LEFT, padx=(0, 12))

        # 计数
        self.count_label = tk.Label(left_bottom, text="0 / 0",
                                   font=('Microsoft YaHei UI', 10, 'bold'),
                                   fg=COLORS['text_primary'],
                                   bg=COLORS['bg_primary'])
        self.count_label.pack(side=tk.LEFT, padx=8)

        # 文件名
        self.filename_label = tk.Label(left_bottom, text="",
                                      font=('Microsoft YaHei UI', 9),
                                      fg=COLORS['text_tertiary'],
                                      bg=COLORS['bg_primary'])
        self.filename_label.pack(side=tk.LEFT, padx=8)

        # 进度条
        self.progress_canvas = tk.Canvas(bottom_bar, height=6, bg=COLORS['border_light'],
                                        highlightthickness=0, bd=0)
        self.progress_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=20)

        # 状态栏
        status_frame = tk.Frame(main_container, bg=COLORS['bg_primary'])
        status_frame.pack(fill=tk.X, pady=(8, 0))

        self.status_label = tk.Label(status_frame, text="就绪",
                                    font=('Microsoft YaHei UI', 9),
                                    fg=COLORS['text_tertiary'],
                                    bg=COLORS['bg_primary'])
        self.status_label.pack(side=tk.LEFT)

        shortcut_text = "快捷键: ← → 切换 | S 保存 | 滚轮缩放 | 拖动平移 | ESC 退出"
        shortcut_label = tk.Label(status_frame, text=shortcut_text,
                                 font=('Microsoft YaHei UI', 9),
                                 fg=COLORS['text_tertiary'],
                                 bg=COLORS['bg_primary'])
        shortcut_label.pack(side=tk.RIGHT)

        # 如果有保存的输出路径，显示
        if self.output_dir and os.path.exists(self.output_dir):
            self.output_dir_display = self.output_dir

    def draw_progress(self, value):
        """绘制进度条"""
        self.progress_canvas.delete("all")
        w = self.progress_canvas.winfo_width()
        h = 6
        if w <= 1:
            return
        # 背景
        r = h // 2
        self.progress_canvas.create_arc((0, 0, h, h), start=90, extent=90,
                                        fill=COLORS['accent'], outline=COLORS['accent'])
        self.progress_canvas.create_arc((0, 0, h, h), start=180, extent=90,
                                        fill=COLORS['accent'], outline=COLORS['accent'])
        fill_w = max(h, int(w * value / 100))
        self.progress_canvas.create_rectangle((r, 0, fill_w, h),
                                             fill=COLORS['accent'], outline=COLORS['accent'])

    def bind_events(self):
        self.root.bind("<Left>", lambda e: self.prev_image())
        self.root.bind("<Right>", lambda e: self.next_image())
        self.root.bind("<Escape>", lambda e: self.root.quit())
        self.root.bind("<s>", lambda e: self.save_current_image())
        self.root.bind("<S>", lambda e: self.save_current_image())
        self.root.bind("<Configure>", self.on_window_resize)

        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", lambda e: self.zoom_in())
        self.canvas.bind("<Button-5>", lambda e: self.zoom_out())

        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_drag_end)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def select_source_dir(self):
        initial_dir = self.current_dir if self.current_dir else os.path.expanduser("~")
        dir_path = filedialog.askdirectory(title="选择包含图片的文件夹", initialdir=initial_dir)
        if dir_path:
            self.current_dir = dir_path
            self.path_label.config(text=dir_path)
            self.config.set("source_dir", dir_path)
            self.config.set("last_index", 0)
            self.current_index = 0
            self.reset_zoom()
            self.load_images()
            self.update_status(f"已加载文件夹")

    def select_output_dir(self):
        initial_dir = self.output_dir if self.output_dir else os.path.expanduser("~")
        dir_path = filedialog.askdirectory(title="选择保存筛选图片的文件夹", initialdir=initial_dir)
        if dir_path:
            self.output_dir = dir_path
            self.config.set("output_dir", dir_path)
            self.update_status(f"输出文件夹已设置")

    def clear_records(self):
        """清空所有记忆记录"""
        self.current_dir = ""
        self.output_dir = ""
        self.image_files = []
        self.current_index = 0
        self.last_image_path = ""
        self.cached_original = None
        self.cached_path = None
        self.zoom_level = 1.0
        self.image_x = 0
        self.image_y = 0

        self.config.config = {
            "source_dir": "",
            "output_dir": "",
            "last_index": 0,
            "last_image_path": "",
            "zoom_level": 1.0
        }
        self.config.save_config()

        self.path_label.config(text="未选择文件夹")
        self.canvas.delete("all")
        self.count_label.config(text="0 / 0")
        self.filename_label.config(text="")
        self.zoom_label.config(text="100%")
        self.draw_progress(0)
        self.update_status("已清空所有记录")

    def load_images(self):
        self.image_files = []
        supported_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp'}

        try:
            for file in Path(self.current_dir).iterdir():
                if file.is_file() and file.suffix.lower() in supported_extensions:
                    self.image_files.append(str(file))

            self.image_files.sort()

            if not self.image_files:
                self.update_status("所选文件夹中没有找到图片文件")
                return

            restored_index = False
            if self.last_image_path:
                try:
                    for i, file_path in enumerate(self.image_files):
                        if file_path == self.last_image_path:
                            self.current_index = i
                            restored_index = True
                            break
                except:
                    pass

            if not restored_index:
                if self.current_index >= len(self.image_files):
                    self.current_index = 0

            self.show_current_image()
            self.update_status(f"已加载 {len(self.image_files)} 张图片" +
                             ("，已恢复上次位置" if restored_index else ""))
        except Exception as e:
            self.update_status(f"加载失败: {str(e)}")

    def show_current_image(self):
        if not self.image_files:
            return

        self.count_label.config(text=f"{self.current_index + 1} / {len(self.image_files)}")

        file_path = self.image_files[self.current_index]
        self.filename_label.config(text=os.path.basename(file_path))

        self.last_image_path = file_path
        self.config.set("last_image_path", file_path)

        try:
            # 使用缓存避免重复读取磁盘
            if self.cached_path != file_path:
                self.cached_original = Image.open(file_path)
                self.cached_path = file_path

            image = self.cached_original
            img_width, img_height = image.size

            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 900
                canvas_height = 600

            # 缓存适应比例，避免重复计算
            self._fit_ratio = min(canvas_width / img_width, canvas_height / img_height)
            final_ratio = self._fit_ratio * self.zoom_level

            new_width = int(img_width * final_ratio)
            new_height = int(img_height * final_ratio)

            if new_width > 0 and new_height > 0:
                # 缩放时用 BILINEAR（快），显示效果已足够
                resized_image = image.resize((new_width, new_height), Image.Resampling.BILINEAR)
            else:
                resized_image = image

            self._displayed_size = (new_width, new_height)

            self.photo_image = ImageTk.PhotoImage(resized_image)

            self.canvas.delete("all")

            x = canvas_width // 2 + self.image_x
            y = canvas_height // 2 + self.image_y
            self.canvas.create_image(x, y, image=self.photo_image, anchor=tk.CENTER, tags="img")

            self._clamp_position()

            zoom_percent = int(self.zoom_level * 100)
            self.zoom_label.config(text=f"{zoom_percent}%")

            progress_value = (self.current_index + 1) / len(self.image_files) * 100
            self.draw_progress(progress_value)

            file_size = os.path.getsize(file_path) / 1024
            self.update_status(f"当前: {os.path.basename(file_path)}  |  "
                             f"{file_size:.1f} KB  |  {img_width}×{img_height}")

        except Exception as e:
            self.update_status(f"加载图片失败: {str(e)}")

    def _clamp_position(self):
        """限制图片拖动范围，保证图片不会完全移出画布"""
        if not hasattr(self, '_displayed_size'):
            return
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        iw, ih = self._displayed_size

        # 图片宽高超过画布时，允许拖动但保留至少100px可见
        # 图片宽高小于画布时，居中不偏移
        margin = 100  # 最少可见像素

        max_x = max((iw + cw) / 2 - margin, 0)
        min_x = -max_x
        max_y = max((ih + ch) / 2 - margin, 0)
        min_y = -max_y

        self.image_x = max(min(self.image_x, max_x), min_x)
        self.image_y = max(min(self.image_y, max_y), min_y)

    def zoom_in(self):
        if self.zoom_level < self.max_zoom:
            self.zoom_level = min(self.zoom_level * self.zoom_factor, self.max_zoom)
            self.config.set("zoom_level", self.zoom_level)
            self.show_current_image()

    def zoom_out(self):
        if self.zoom_level > self.min_zoom:
            self.zoom_level = max(self.zoom_level / self.zoom_factor, self.min_zoom)
            self.config.set("zoom_level", self.zoom_level)
            self.show_current_image()

    def reset_zoom(self):
        self.zoom_level = 1.0
        self.image_x = 0
        self.image_y = 0
        self.config.set("zoom_level", self.zoom_level)
        self.show_current_image()

    def on_mouse_wheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def on_drag_start(self, event):
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.canvas.config(cursor="fleur")

    def on_drag_motion(self, event):
        if self.is_dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.image_x += dx
            self.image_y += dy
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            # 限制范围后用 coords 移动（比 delete+create 快）
            self._clamp_position()
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            self.canvas.coords("img", cw // 2 + self.image_x, ch // 2 + self.image_y)

    def on_drag_end(self, event):
        self.is_dragging = False
        self.canvas.config(cursor="")

    def on_window_resize(self, event):
        if event.widget == self.root:
            if hasattr(self, '_resize_after_id'):
                self.root.after_cancel(self._resize_after_id)
            self._resize_after_id = self.root.after(100, self.on_resize_complete)

    def on_resize_complete(self):
        self.image_x = 0
        self.image_y = 0
        self.show_current_image()

    def prev_image(self):
        if self.image_files and self.current_index > 0:
            self.current_index -= 1
            self.config.set("last_index", self.current_index)
            self.reset_zoom()

    def next_image(self):
        if self.image_files and self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.config.set("last_index", self.current_index)
            self.reset_zoom()

    def save_current_image(self):
        if not self.image_files:
            self.show_toast("没有可保存的图片", "warning")
            return

        if not self.output_dir:
            self.show_toast("请先设置输出文件夹", "warning")
            return

        os.makedirs(self.output_dir, exist_ok=True)

        source_path = self.image_files[self.current_index]
        filename = os.path.basename(source_path)
        dest_path = os.path.join(self.output_dir, filename)

        # 检查是否已存在同名文件
        if os.path.exists(dest_path):
            self.show_toast(f"已存在: {filename}", "warning")
            self.update_status(f"已存在，跳过: {filename}")
            return

        try:
            shutil.copy2(source_path, dest_path)
            self.show_toast(f"✓ 已保存: {filename}", "success")
            self.update_status(f"已保存: {filename}")
        except Exception as e:
            self.show_toast(f"保存失败: {str(e)}", "error")
            self.update_status(f"保存失败: {str(e)}")

    def update_status(self, message):
        self.status_label.config(text=message)

    def show_toast(self, message, msg_type="info"):
        """现代化提示框"""
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)

        toast_width = 280
        toast_height = 44

        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        x = root_x + root_width - toast_width - 20
        y = root_y + root_height - toast_height - 50
        toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")

        # 颜色配置（柔和的现代化风格）
        if msg_type == "success":
            bg_color = "#E8F8EE"
            text_color = "#00B42A"
        elif msg_type == "warning":
            bg_color = "#FFF7E6"
            text_color = "#FF7D00"
        elif msg_type == "error":
            bg_color = "#FFECE8"
            text_color = "#F53F3F"
        else:
            bg_color = "#E8F3FF"
            text_color = "#1677FF"

        toast.configure(bg=bg_color)
        label = tk.Label(toast, text=message, bg=bg_color, fg=text_color,
                        font=('Microsoft YaHei UI', 10), padx=20, pady=10)
        label.pack(fill=tk.BOTH, expand=True)

        toast.after(2000, toast.destroy)
        toast.attributes('-topmost', True)
        toast.lift()

    def on_close(self):
        if self.image_files:
            self.config.set("last_index", self.current_index)
        self.root.quit()
        self.root.destroy()


def main():
    root = tk.Tk()
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = ImageViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
