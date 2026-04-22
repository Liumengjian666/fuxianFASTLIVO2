#!/bin/bash

# FAST-LIVO2 NTU VIRAL 数据集运行脚本
# 功能：启动 roscore、运行算法、播放 bag 文件

BAG_PATH="/home/liumengjian/datasets/LVO/nya_01/nya_01.bag"
LAUNCH_FILE="mapping_ouster_ntu.launch"
PACKAGE_NAME="fast_livo"

echo "=========================================="
echo "FAST-LIVO2 - NTU VIRAL Dataset (nya_01)"
echo "=========================================="
echo ""

# 检查 bag 文件是否存在
if [ ! -f "$BAG_PATH" ]; then
    echo "❌ 错误: Bag 文件不存在: $BAG_PATH"
    exit 1
fi

# 清理之前的 ROS 进程
echo "🧹 清理残留进程..."
pkill -9 -f roslaunch 2>/dev/null
pkill -9 -f fastlivo 2>/dev/null
pkill -9 -f rviz 2>/dev/null
pkill -9 -f rosbag 2>/dev/null
sleep 2

# 检查并启动 roscore
echo "📡 检查 roscore..."
if ! pgrep -x roscore > /dev/null; then
    echo "   启动 roscore..."
    roscore &
    sleep 3
else
    echo "   ✓ roscore 已运行"
fi

# Source 环境
source /home/liumengjian/catkin_ws/devel/setup.bash

# 启动 FAST-LIVO2
echo "🚀 启动 FAST-LIVO2..."
roslaunch $PACKAGE_NAME $LAUNCH_FILE &
FASTLIVO_PID=$!
sleep 5

# 播放 bag 文件（循环播放）
echo "📼 播放 bag 文件: $BAG_PATH"
rosbag play "$BAG_PATH" --clock --loop &
BAG_PID=$!

echo ""
echo "=========================================="
echo "✅ 系统已启动！"
echo "=========================================="
echo "• RViz 应显示："
echo "  - 左下角：彩色 RGB 图像 (/rgb_img)"
echo "  - 右侧：红色点云建图 (/cloud_registered)"
echo ""
echo "• 按 Ctrl+C 停止所有进程"
echo "=========================================="

# 等待用户中断
trap 'echo ""; echo "🛑 正在停止..."; kill $BAG_PID $FASTLIVO_PID 2>/dev/null; pkill -9 -f roslaunch; pkill -9 -f rosbag; pkill -9 -f rviz; exit 0' INT

wait
