#!/bin/bash

# 检查 NTU VIRAL 数据集中图像的编码格式

BAG_PATH="/home/liumengjian/datasets/LVO/nya_01/nya_01.bag"

echo "=========================================="
echo "检查图像编码格式"
echo "=========================================="
echo ""

# 启动 roscore（如果未运行）
if ! pgrep -x roscore > /dev/null; then
    echo "📡 启动 roscore..."
    roscore &
    sleep 2
fi

# Source 环境
source /home/liumengjian/catkin_ws/devel/setup.bash

# 播放 bag 并检查图像编码
echo "📼 播放 bag 文件并检查图像话题..."
rosbag play "$BAG_PATH" --topics /left/image_raw --clock &
BAG_PID=$!
sleep 3

# 获取图像编码信息
echo ""
echo "📊 图像话题信息："
rostopic info /left/image_raw

echo ""
echo "🔍 图像编码格式（采样第一条消息）："
rostopic echo /left/image_raw -n 1 | grep encoding

# 停止播放
kill $BAG_PID 2>/dev/null

echo ""
echo "=========================================="
echo "检查完成！"
echo "=========================================="
