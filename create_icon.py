#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图标生成器 - 为图片筛选工具创建图标
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """创建图片筛选工具图标"""
    # 图标尺寸
    sizes = [16, 32, 48, 64, 128, 256]
    
    # 创建不同尺寸的图标
    for size in sizes:
        # 创建图像
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 计算缩放比例
        scale = size / 256
        
        # 绘制圆形背景
        margin = int(10 * scale)
        draw.ellipse([margin, margin, size - margin, size - margin], 
                    fill='#0078d4', outline='#005a9e', width=int(3 * scale))
        
        # 绘制图片图标
        # 外框
        box_margin = int(40 * scale)
        box_width = int(180 * scale)
        box_height = int(140 * scale)
        box_x = (size - box_width) // 2
        box_y = (size - box_height) // 2
        
        # 绘制白色背景的图片框
        draw.rectangle([box_x, box_y, box_x + box_width, box_y + box_height], 
                      fill='white', outline='#cccccc', width=int(2 * scale))
        
        # 绘制图片内容（简化的山水画）
        # 山
        mountain_y = box_y + int(80 * scale)
        draw.polygon([
            (box_x + int(20 * scale), box_y + box_height - int(20 * scale)),
            (box_x + int(60 * scale), mountain_y),
            (box_x + int(100 * scale), box_y + box_height - int(20 * scale))
        ], fill='#4a90e2')
        
        draw.polygon([
            (box_x + int(80 * scale), box_y + box_height - int(20 * scale)),
            (box_x + int(120 * scale), mountain_y + int(20 * scale)),
            (box_x + int(160 * scale), box_y + box_height - int(20 * scale))
        ], fill='#357abd')
        
        # 太阳
        sun_x = box_x + int(140 * scale)
        sun_y = box_y + int(40 * scale)
        sun_radius = int(15 * scale)
        draw.ellipse([sun_x - sun_radius, sun_y - sun_radius, 
                     sun_x + sun_radius, sun_y + sun_radius], 
                    fill='#ffd700')
        
        # 保存图标
        icon_path = os.path.join(os.path.dirname(__file__), f'icon_{size}.png')
        img.save(icon_path, 'PNG')
        print(f'已创建图标: {icon_path}')
    
    # 创建ICO文件（包含多个尺寸）
    ico_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
    
    # 加载不同尺寸的图像
    icon_images = []
    for size in sizes:
        icon_path = os.path.join(os.path.dirname(__file__), f'icon_{size}.png')
        if os.path.exists(icon_path):
            icon_images.append(Image.open(icon_path))
    
    # 保存为ICO格式
    if icon_images:
        icon_images[0].save(ico_path, format='ICO', 
                          sizes=[(img.size[0], img.size[1]) for img in icon_images])
        print(f'已创建ICO图标: {ico_path}')
    
    # 清理临时PNG文件
    for size in sizes:
        icon_path = os.path.join(os.path.dirname(__file__), f'icon_{size}.png')
        if os.path.exists(icon_path):
            os.remove(icon_path)
            print(f'已清理临时文件: {icon_path}')

if __name__ == '__main__':
    create_icon()