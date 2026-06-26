# 图片筛选工具 v4.0

一个简洁的图片浏览与筛选桌面工具，支持快速浏览文件夹中的图片并筛选保存到指定目录。

## 功能特点

- **快速浏览** - 支持 JPG、PNG、BMP、GIF、TIFF、WebP 等常见格式
- **图片缩放** - 鼠标滚轮缩放、按钮缩放，范围 10% - 1000%
- **拖动查看** - 按住鼠标左键拖动图片查看细节，带边界限制
- **筛选保存** - 一键将当前图片复制到输出文件夹
- **记忆系统** - 自动记录上次查看的文件夹和图片位置，下次打开直接跳转
- **清空记录** - 一键清除所有保存的设置和记录
- **现代化 UI** - 圆角设计、侧边栏布局、柔和配色

## 截图

<!-- TODO: 添加截图 -->
<img width="1919" height="1030" alt="image" src="https://github.com/user-attachments/assets/20ef4aee-b340-40fc-b6c7-44b8b9eebd4e" />



## 下载

前往 [Releases](../../releases) 页面下载最新版本的 exe 文件。

## 使用方法

1. 下载并运行 `图片筛选工具.exe`
2. 点击"选择图片文件夹"或侧边栏"打开文件夹"
3. 点击"设置输出文件夹"选择筛选图片的保存位置
4. 使用 `←` `→` 键或按钮切换图片
5. 点击"保存"按钮将当前图片保存到输出文件夹

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `←` | 上一张图片 |
| `→` | 下一张图片 |
| 鼠标滚轮 | 缩放图片 |
| 鼠标拖动 | 平移图片 |
| `ESC` | 退出程序 |

## 从源码运行

### 环境要求

- Python 3.8+
- Pillow

### 安装依赖

```bash
pip install Pillow
```

### 运行

```bash
python image_viewer.py
```

### 打包为 exe

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "图片筛选工具" --icon icon.ico image_viewer.py
```

## 项目结构

```
├── image_viewer.py         # 主程序源码
├── create_icon.py          # 图标生成脚本
├── icon.ico                # 程序图标
├── requirements.txt        # 依赖清单
├── LICENSE                 # MIT 许可证
└── README.md
```

## 技术栈

- **GUI**: Tkinter
- **图片处理**: Pillow
- **打包**: PyInstaller

## 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

## 贡献

欢迎提交 Issue 和 Pull Request。

## 作者

- [Likook](https://github.com/Likook2025)
