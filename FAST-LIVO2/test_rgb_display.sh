#!/bin/bash

# 快速测试脚本：验证彩色图像显示修复

echo "=========================================="
echo "FAST-LIVO2 彩色图像显示测试"
echo "=========================================="
echo ""

# 清理进程
echo "🧹 清理进程..."
pkill -9 -f roslaunch 2>/dev/null
pkill -9 -f fastlivo 2>/dev/null
pkill -9 -f rviz 2>/dev/null
pkill -9 -f rosbag 2>/dev/null
sleep 2

# Source 环境
source /home/liumengjian/catkin_ws/devel/setup.bash

# 启动 roscore
if ! pgrep -x roscore > /dev/null; then
    echo "📡 启动 roscore..."
    roscore &
    sleep 3
fi

echo ""
echo "🚀 启动 FAST-LIVO2（NTU VIRAL 配置）..."
roslaunch fast_livo mapping_ouster_ntu.launch &
sleep 5

echo ""
echo "📼 播放 bag 文件（只播放前30秒用于测试）..."
rosbag play /home/liumengjian/datasets/LVO/nya_01/nya_01.bag --clock --duration 30 &
sleep 5

echo ""
echo "=========================================="
echo "✅ 测试环境已就绪！"
echo "=========================================="
echo ""
echo "请在 RViz 中检查："
echo "  1. 左下角 Image 面板是否显示**彩色**图像"
echo "  2. 右侧点云是否为红色"
echo ""
echo "查看话题信息："
echo "  rostopic info /rgb_img"
echo "  rostopic hz /rgb_img"
echo ""
echo "按 Ctrl+C 停止测试"
echo "=========================================="

wait
