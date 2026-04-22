# RGB彩色地图显示与保存指南

## 功能说明

本指南介绍如何在RViz中显示带相机图像的彩色点云地图，以及如何保存RGB彩色地图。

## 1. 配置文件设置

编辑 `config/NTU_VIRAL.yaml`（或其他数据集配置文件）：

```yaml
common:
  img_en: 1                # 启用图像输入
  img_topic: "/left/image_raw"

vio:
  exposure_estimate_en: true  # 启用曝光估计，提升颜色质量

pcd_save:
  pcd_save_en: true        # 启用地图保存
  interval: -1             # -1表示结束时保存，正数表示每隔N帧保存
  filter_size_pcd: 0.15    # PCD降采样体素大小
  type: 0                  # 0:世界坐标系, 1:机体坐标系

publish:
  dense_map_en: true       # 启用密集地图发布
```

## 2. 编译代码

```bash
cd ~/catkin_ws
catkin_make -j2
source devel/setup.bash
```

## 3. 运行系统

```bash
# 终端1: 启动FAST-LIVO2
roslaunch fast_livo mapping_ouster_ntu.launch

# 终端2: 播放数据集
rosbag play YOUR_DATASET.bag
```

## 4. RViz配置

### 4.1 打开配置文件

```bash
rviz -d /home/liumengjian/catkin_ws/src/FAST-LIVO2/rviz_cfg/ntu_viral.rviz
```

### 4.2 手动配置（如需要）

在RViz中添加以下显示插件：

#### (1) RGB彩色点云地图
- **Display Type**: PointCloud2
- **Name**: surround
- **Topic**: `/cloud_registered`
- **Color Transformer**: `RGB8`
- **Style**: Points
- **Size (m)**: 0.005
- **Decay Time**: 10000

#### (2) 相机图像
- **Display Type**: Image
- **Name**: Image
- **Image Topic**: `/rgb_img`
- **Transport Hint**: raw

#### (3) 其他可选显示
- **Path**: 订阅 `/path`，显示轨迹
- **Axes**: 显示坐标系
- **Odometry**: 订阅 `/aft_mapped_to_init`，显示位姿

## 5. 地图保存

系统运行结束后，自动保存RGB彩色地图：

- **原始地图**: `Log/pcd/all_raw_points.pcd`
- **降采样地图**: `Log/pcd/all_downsampled_points.pcd`
- **激光雷达位姿**: `Log/pcd/lidar_poses.txt`
- **轨迹**: `Log/result/<seq_name>.txt`

## 6. 查看保存的地图

```bash
# 使用pcl_viewer查看
pcl_viewer Log/pcd/all_downsampled_points.pcd

# 使用CloudCompare查看
cloudcompare Log/pcd/all_downsampled_points.pcd
```

## 7. RViz窗口布局

参考截图效果，推荐以下布局：

- **主窗口**: 3D View，显示RGB点云地图
- **右侧/底部面板**: Image插件，显示相机图像帧
- 可拖动Image面板调整大小和位置

## 8. 关键话题说明

| 话题名 | 类型 | 说明 |
|--------|------|------|
| `/cloud_registered` | PointCloud2 (XYZRGB) | RGB彩色点云地图 |
| `/rgb_img` | Image (BGR8) | 相机图像 |
| `/cloud_visual_sub_map_before` | PointCloud2 | 视觉子地图 |
| `/planes` | MarkerArray | 体素平面可视化 |
| `/path` | Path | 轨迹 |
| `/aft_mapped_to_init` | Odometry | 位姿 |

## 9. 常见问题

### Q1: 点云没有颜色？
- 检查 `common/img_en` 是否为 1
- 确认 `img_topic` 是否正确
- 查看RViz中 Color Transformer 是否设为 `RGB8`

### Q2: 图像不显示？
- 检查RViz中 Image Topic 是否为 `/rgb_img`
- 确认相机驱动正常发布图像
- 查看终端是否有图像回调日志

### Q3: 地图未保存？
- 确认 `pcd_save/pcd_save_en: true`
- 检查 `Log/pcd/` 目录是否存在
- 查看终端是否有 "Raw point cloud data saved to:" 提示

### Q4: 性能问题？
- 减少 `publish/pub_scan_num` 值
- 降低图像分辨率（修改 `vio` 参数）
- 关闭不必要的显示插件

## 10. 代码实现细节

### RGB点云生成位置
- 文件: `src/LIVMapper.cpp`
- 函数: `publish_frame_world()`
- 逻辑: 将LiDAR点投影到相机坐标系，采样图像RGB值

### 图像发布位置
- 文件: `src/LIVMapper.cpp`
- 函数: `publish_img_rgb()`
- 话题: `/rgb_img`

### 地图保存位置
- 文件: `src/LIVMapper.cpp`
- 函数: `savePCD()`
- 格式: PointCloudXYZRGB (二进制PCD)
