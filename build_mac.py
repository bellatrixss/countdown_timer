import os
import platform
import subprocess

# 确保我们在正确的目录中
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 应用名称
app_name = "倒计时"

# 图标文件 (如果有)
icon_file = "icon.icns"  # 需要创建一个.icns格式的图标文件

# 检查是否在Mac上运行
if platform.system() != "Darwin":
    print("此脚本需要在Mac OS上运行")
    exit(1)

# 构建命令
cmd = [
    "pyinstaller",
    "--name={}".format(app_name),
    "--windowed",  # 创建一个GUI应用而不是控制台应用
    "--onefile",   # 创建单个可执行文件
    "--clean",     # 清理临时文件
]

# 如果有图标文件，添加图标
if os.path.exists(icon_file):
    cmd.append("--icon={}".format(icon_file))

# 添加主程序文件
cmd.append("countdown_timer.py")

# 执行命令
subprocess.call(cmd)

print("打包完成！应用程序位于 dist 文件夹中。")