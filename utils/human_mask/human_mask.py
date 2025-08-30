import os
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Union, Tuple, Dict

class HumanMask:
    def __init__(self):
        # 初始化模型路径
        self.model_path = None
        
        # 尝试加载预训练的人体检测模型
        try:
            # 在实际应用中，这里应该加载YOLO或其他预训练的人体检测模型
            # 由于我们没有实际的模型文件，使用一个简单的实现
            pass
        except Exception as e:
            print(f"加载人体检测模型时出错: {e}")

    def detect_human(self, image_path: str, threshold: float = 0.5) -> bool:
        """检测图像中是否包含人体"""
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 简单的人体检测实现
            # 在实际应用中，这里应该使用更复杂的算法或预训练模型
            
            # 计算图像的边缘
            edges = cv2.Canny(gray, 100, 200)
            
            # 计算边缘密度
            edge_density = np.sum(edges) / (image.shape[0] * image.shape[1])
            
            # 根据边缘密度判断是否包含人体
            # 这个阈值是经验值，需要根据实际情况调整
            return edge_density > 10
        except Exception as e:
            print(f"人体检测时出错: {e}")
            return False

    def segment_human(self, image_path: str, output_path: str = None) -> Optional[np.ndarray]:
        """分割图像中的人体区域"""
        try:
            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # 转换为HSV颜色空间
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 简单的皮肤颜色检测（在实际应用中，这应该使用更复杂的算法）
            # 定义皮肤颜色范围（HSV）
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            
            # 创建掩码
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # 进行形态学操作以改善掩码
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # 如果提供了输出路径，保存分割结果
            if output_path:
                # 创建透明背景的结果图像
                result = cv2.bitwise_and(image, image, mask=mask)
                
                # 转换为RGBA格式以支持透明度
                b, g, r = cv2.split(result)
                a = mask
                rgba = [r, g, b, a]
                dst = cv2.merge(rgba, 4)
                
                # 保存结果
                cv2.imwrite(output_path, dst)
            
            return mask
        except Exception as e:
            print(f"人体分割时出错: {e}")
            return None

    def get_human_pose(self, image_path: str) -> Optional[Dict]:
        """估计图像中人体的姿态"""
        try:
            # 在实际应用中，这里应该使用预训练的姿态估计模型
            # 由于我们没有实际的模型文件，返回一个模拟的姿态
            return {
                "keypoints": [
                    {"x": 100, "y": 50, "score": 0.9},  # 头部
                    {"x": 80, "y": 120, "score": 0.8},  # 左肩
                    {"x": 120, "y": 120, "score": 0.8},  # 右肩
                    {"x": 70, "y": 200, "score": 0.7},  # 左肘
                    {"x": 130, "y": 200, "score": 0.7},  # 右肘
                    {"x": 90, "y": 280, "score": 0.6},  # 左手
                    {"x": 110, "y": 280, "score": 0.6},  # 右手
                    {"x": 80, "y": 300, "score": 0.8},  # 左髋
                    {"x": 120, "y": 300, "score": 0.8},  # 右髋
                    {"x": 70, "y": 400, "score": 0.7},  # 左膝
                    {"x": 130, "y": 400, "score": 0.7},  # 右膝
                    {"x": 80, "y": 500, "score": 0.6},  # 左脚
                    {"x": 120, "y": 500, "score": 0.6}   # 右脚
                ],
                "skeleton": [
                    [0, 1], [0, 2], [1, 3], [2, 4], [3, 5], [4, 6],  # 上半身
                    [1, 7], [2, 8], [7, 9], [8, 10], [9, 11], [10, 12]  # 下半身
                ]
            }
        except Exception as e:
            print(f"姿态估计时出错: {e}")
            return None

    def visualize_mask(self, image_path: str, mask: np.ndarray, output_path: str) -> str:
        """可视化人体掩码"""
        try:
            # 读取原始图像
            image = cv2.imread(image_path)
            
            # 创建彩色掩码
            color_mask = np.zeros_like(image)
            color_mask[mask > 0] = [0, 255, 0]  # 绿色
            
            # 将掩码叠加到原始图像上
            result = cv2.addWeighted(image, 0.7, color_mask, 0.3, 0)
            
            # 保存结果
            cv2.imwrite(output_path, result)
            
            return output_path
        except Exception as e:
            print(f"可视化掩码时出错: {e}")
            return image_path

    def visualize_pose(self, image_path: str, pose: Dict, output_path: str) -> str:
        """可视化人体姿态"""
        try:
            # 读取原始图像
            image = cv2.imread(image_path)
            
            # 绘制关键点
            for keypoint in pose.get("keypoints", []):
                x, y = int(keypoint["x"]), int(keypoint["y"])
                cv2.circle(image, (x, y), 5, (0, 0, 255), -1)  # 红色圆点
            
            # 绘制骨架
            for bone in pose.get("skeleton", []):
                pt1 = pose["keypoints"][bone[0]]
                pt2 = pose["keypoints"][bone[1]]
                x1, y1 = int(pt1["x"]), int(pt1["y"])
                x2, y2 = int(pt2["x"]), int(pt2["y"])
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # 绿色线条
            
            # 保存结果
            cv2.imwrite(output_path, image)
            
            return output_path
        except Exception as e:
            print(f"可视化姿态时出错: {e}")
            return image_path

# 创建全局实例
human_mask_instance = HumanMask()