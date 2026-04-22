#!/bin/bash
# FAST-LIVO2 清理脚本 - 彻底终止所有相关进程

echo "正在停止所有FAST-LIVO2相关进程..."

# 停止所有ROS相关进程
pkill -9 -f "roslaunch fast_livo"
pkill -9 -f "fastlivo_mapping"
pkill -9 -f "rosbag play"
pkill -9 -f "rviz"
pkill -9 -f roscore
# 等待进程完全退出
sleep 1

# 检查是否还有残留进程
REMAINING=$(ps aux | grep -E "(fastlivo|rosbag|rviz)" | grep -v grep | wc -l)

if [ $REMAINING -eq 0 ]; then
    echo "✓ 所有进程已清理完成"
else
    echo "⚠ 仍有 $REMAINING 个进程在运行"
    ps aux | grep -E "(fastlivo|rosbag|rviz)" | grep -v grep
    echo "正在强制清理..."
    pkill -9 -f "fastlivo"
    pkill -9 -f "rosbag"
    pkill -9 -f "rviz"
fi

echo "清理完成！"