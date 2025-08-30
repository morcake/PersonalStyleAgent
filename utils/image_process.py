import cv2
import numpy as np
from PIL import Image
import os

class ImageProcess:
    def __init__(self):
        pass

    def resize_image(self, image_path: str, width: int, height: int, save_path: str = None) -> np.ndarray:
        """调整图像大小"""
        image = cv2.imread(image_path)
        resized_image = cv2.resize(image, (width, height))
        
        if save_path:
            cv2.imwrite(save_path, resized_image)
            
        return resized_image

    def crop_image(self, image_path: str, x: int, y: int, width: int, height: int, save_path: str = None) -> np.ndarray:
        """裁剪图像"""
        image = cv2.imread(image_path)
        cropped_image = image[y:y+height, x:x+width]
        
        if save_path:
            cv2.imwrite(save_path, cropped_image)
            
        return cropped_image

    def enhance_image(self, image_path: str, contrast: float = 1.0, brightness: int = 0, save_path: str = None) -> np.ndarray:
        """增强图像对比度和亮度"""
        image = cv2.imread(image_path)
        enhanced_image = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
        
        if save_path:
            cv2.imwrite(save_path, enhanced_image)
            
        return enhanced_image

    def rotate_image(self, image_path: str, angle: float, save_path: str = None) -> np.ndarray:
        """旋转图像"""
        image = cv2.imread(image_path)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        
        # 计算旋转矩阵
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_image = cv2.warpAffine(image, M, (w, h))
        
        if save_path:
            cv2.imwrite(save_path, rotated_image)
            
        return rotated_image

    def convert_to_grayscale(self, image_path: str, save_path: str = None) -> np.ndarray:
        """将图像转换为灰度图"""
        image = cv2.imread(image_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if save_path:
            cv2.imwrite(save_path, gray_image)
            
        return gray_image

    def save_image(self, image: np.ndarray, save_path: str) -> None:
        """保存图像"""
        cv2.imwrite(save_path, image)

    def pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """将PIL图像转换为OpenCV格式"""
        # PIL图像是RGB格式，OpenCV是BGR格式
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def cv2_to_pil(self, cv2_image: np.ndarray) -> Image.Image:
        """将OpenCV图像转换为PIL格式"""
        # OpenCV图像是BGR格式，PIL是RGB格式
        return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

    def blend_images(self, image1_path: str, image2_path: str, alpha: float = 0.5, save_path: str = None) -> np.ndarray:
        """混合两张图像"""
        image1 = cv2.imread(image1_path)
        image2 = cv2.imread(image2_path)
        
        # 确保两张图像大小相同
        if image1.shape != image2.shape:
            image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
        
        blended_image = cv2.addWeighted(image1, alpha, image2, 1 - alpha, 0)
        
        if save_path:
            cv2.imwrite(save_path, blended_image)
            
        return blended_image

    def remove_background(self, image_path: str, save_path: str = None) -> np.ndarray:
        """移除图像背景（简单实现）"""
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 阈值分割
        _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # 创建透明背景
        result = cv2.bitwise_and(image, image, mask=mask)
        
        if save_path:
            # 保存为PNG格式以支持透明度
            result_pil = self.cv2_to_pil(result)
            result_pil.save(save_path, "PNG")
            
        return result

# 创建全局实例
image_process_instance = ImageProcess()

# 导出函数
def image_process() -> ImageProcess:
    """返回图像处理实例"""
    return image_process_instance