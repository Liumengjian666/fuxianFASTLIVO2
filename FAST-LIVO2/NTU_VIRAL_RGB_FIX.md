# NTU VIRAL 数据集彩色图像显示修复说明

## 问题描述
NTU VIRAL 数据集中的相机图像为 **Bayer 格式**（`bayer_rggb8`），但 FAST-LIVO2 原始代码直接将其转换为 BGR，导致 RViz 中显示为**灰度图像**而非彩色图像。

## 解决方案

### 1. 代码修改
修改了 `src/LIVMapper.cpp` 中的 `getImageFromMsg()` 函数，添加了对 Bayer 格式的自动检测和去马赛克转换：

**支持的格式：**
- `bayer_rggb8` → RGB（最常用）
- `bayer_bggr8` → RGB
- `bayer_gbrg8` → RGB
- `bayer_grbg8` → RGB
- `mono8` / `8UC1` → BGR（灰度图转彩色）
- 其他格式 → BGR（直接转换）

**关键实现：**
```cpp
if (img_msg->encoding == "bayer_rggb8") {
  cv::Mat bayer_img = cv_bridge::toCvCopy(img_msg, img_msg->encoding)->image;
  cv::cvtColor(bayer_img, img, cv::COLOR_BayerBG2RGB);  // OpenCV 命名相反
}
```

> ⚠️ **注意**：OpenCV 的 Bayer 编码命名与标准相反，`bayer_rggb8` 需使用 `COLOR_BayerBG2RGB`。

### 2. 配置文件
无需修改 `NTU_VIRAL.yaml`，保持原有配置：
```yaml
common:
  img_topic: "/left/image_raw"  # 订阅原始 Bayer 图像
  img_en: 1                      # 启用图像处理
```

### 3. RViz 配置
使用专用的 RGB 配置文件：`rviz_cfg/ntu_viral_rgb.rviz`
- Image 插件订阅 `/rgb_img` 话题
- PointCloud2 插件使用 `RGB8` 颜色转换器显示红色点云

## 使用方法

### 方法一：一键运行脚本（推荐）
```bash
cd /home/liumengjian/catkin_ws/src/FAST-LIVO2
./run_ntu_viral.sh
```

该脚本会自动：
1. 清理残留进程
2. 启动 roscore
3. 运行 FAST-LIVO2
4. 循环播放 bag 文件

### 方法二：手动运行
```bash
# Terminal 1: 启动 roscore
roscore

# Terminal 2: 运行 FAST-LIVO2
cd ~/catkin_ws
source devel/setup.bash
roslaunch fast_livo mapping_ouster_ntu.launch

# Terminal 3: 播放 bag 文件
rosbag play /home/liumengjian/datasets/LVO/nya_01/nya_01.bag --clock --loop
```

### 检查图像编码（可选）
```bash
./check_image_encoding.sh
```

## 预期效果

✅ **左下角**：彩色 RGB 图像（`/rgb_img`）  
✅ **右侧**：红色点云建图（`/cloud_registered`，Color Transformer: RGB8）

## 调试技巧

### 如果仍显示灰度图：
1. 检查图像编码：
   ```bash
   rostopic echo /left/image_raw -n 1 | grep encoding
   ```

2. 检查 `/rgb_img` 话题：
   ```bash
   rostopic info /rgb_img
   ```

3. 在 RViz 中确认：
   - Image 插件的 `Transport Hint` 设为 `raw`
   - PointCloud2 插件的 `Color Transformer` 设为 `RGB8`

### 查看实时日志：
```bash
rosrun fast_livo fastlivo_mapping 2>&1 | tee /tmp/fastlivo.log
```

## 技术细节

### Bayer 格式说明
Bayer 是一种色彩滤镜阵列，每个像素只记录一种颜色（R、G 或 B）。需要通过**去马赛克**（demosaicing）算法重建完整 RGB 图像。

NTU VIRAL 使用的相机传感器输出 `bayer_rggb8` 格式：
```
R G R G ...
G B G B ...
R G R G ...
...
```

### OpenCV 转换代码对应关系
| ROS 编码       | OpenCV 转换代码          |
|---------------|------------------------|
| bayer_rggb8   | COLOR_BayerBG2RGB      |
| bayer_bggr8   | COLOR_BayerRG2RGB      |
| bayer_gbrg8   | COLOR_BayerGR2RGB      |
| bayer_grbg8   | COLOR_BayerGB2RGB      |

> 这是因为 OpenCV 假设输入的是**目标格式**，而 ROS 描述的是**源格式**。

## 修改文件清单
1. `src/LIVMapper.cpp` - 修改 `getImageFromMsg()` 函数
2. `launch/mapping_ouster_ntu.launch` - 保持简洁（无需 image_proc）
3. `run_ntu_viral.sh` - 新增一键运行脚本
4. `check_image_encoding.sh` - 新增诊断脚本

## 参考资料
- [OpenCV Color Conversion Codes](https://docs.opencv.org/master/d7/d1b/group__imgproc__misc.html#ga4e0972be5de079fed4e3a10e24ef5ef0)
- [ROS image_proc](http://wiki.ros.org/image_proc)
- [NTU VIRAL Dataset](https://ntu-aris.github.io/ntu_viral_dataset/)
