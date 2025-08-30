import os
import json
from typing import Dict, List, Optional, Union
from PIL import Image
import numpy as np
from utils.flux_vton import run_vton
from utils.metrics import VQAScore, ClipScore
from utils.image_process import image_process
from utils.human_mask import human_mask_instance
from config.config import STATIC_FOLDER, MAX_FLUX_VTON_ITERATIONS, VTON_GUIDANCE_SCALE

class VirtualTryOnAgent:
    def __init__(self):
        # 初始化虚拟试穿和评估组件
        self.vqa_score = VQAScore()
        self.clip_score = ClipScore()

    def try_on_clothing(self, person_image_path: str, clothing_image_path: str, 
                       clothing_description: str = "", iterations: int = None, 
                       guidance_scale: float = None) -> Dict:
        """执行虚拟试穿"""
        try:
            # 使用配置中的参数，如果未提供
            if iterations is None:
                iterations = MAX_FLUX_VTON_ITERATIONS
            if guidance_scale is None:
                guidance_scale = VTON_GUIDANCE_SCALE

            # 构建garment_info字典，符合flux_vton.py中run_vton函数的预期格式
            garment_info = {
                "category": "upper_body",  # 默认类别，可以根据实际情况调整
                "prompt": clothing_description if clothing_description else "简约风格的服装",
                "garments": [{
                    "id": 0,
                    "path": clothing_image_path
                }]
            }

            # 调用虚拟试穿函数，使用正确的参数
            result = run_vton(
                garment_info=garment_info,
                human_image_path=person_image_path,
                gender="female"  # 默认性别，可以根据实际情况调整
            )

            # 检查结果
            if not result or "vton_results" not in result or not result["vton_results"]:
                print(f"虚拟试穿失败: 未返回有效结果")
                return {"success": False, "error": "虚拟试穿失败"}

            # 获取最佳结果
            best_vton_result = result["vton_results"][0]
            result_image_path = best_vton_result["vton_path"]
            score = best_vton_result["score"]

            print(f"虚拟试穿成功，最佳结果评分: {score}")
            return {
                "success": True,
                "result_image": result_image_path,
                "iteration_results": [result_image_path],  # 简化处理，只返回最佳结果
                "clip_scores": [score],  # 简化处理，只返回最佳评分
                "best_iteration": 0
            }
        except Exception as e:
            print(f"执行虚拟试穿时出错: {e}")
            return {"success": False, "error": str(e)}

    def evaluate_try_on_result(self, person_image_path: str, clothing_image_path: str, 
                              try_on_result_image: str, clothing_description: str = "") -> Dict:
        """评估虚拟试穿结果"""
        try:
            # 读取图像
            person_image = Image.open(person_image_path)
            clothing_image = Image.open(clothing_image_path)
            result_image = Image.open(try_on_result_image)

            # 生成评估描述
            if not clothing_description:
                clothing_description = "一件服装"

            # 使用VQA评分器评估结果
            vqa_prompt = f"这件{clothing_description}穿在模特身上看起来自然吗？整体效果如何？"
            vqa_result = self.vqa_score.score_image(try_on_result_image, vqa_prompt)

            # 使用CLIP评分器评估结果
            clip_score = self.clip_score.score(try_on_result_image, clothing_description)

            # 人体检测和分割评估
            human_detection = human_mask_instance.detect_human(result_image)
            human_segmentation = human_mask_instance.segment_human(result_image)

            # 构建评估结果
            evaluation = {
                "vqa_evaluation": vqa_result,
                "clip_score": float(clip_score),  # 转换为Python原生浮点数
                "human_detection": {
                    "has_human": human_detection["has_human"],
                    "confidence": human_detection["confidence"]
                },
                "segmentation_quality": {
                    "has_segmentation": len(human_segmentation["mask"]) > 0,
                    "area_percentage": human_segmentation["area_percentage"]
                }
            }

            # 添加总体评分（1-10分）
            # 这是一个简化的评分逻辑，实际应用中可能需要更复杂的评分算法
            overall_score = min(10, max(1, int(clip_score * 5 + 5)))
            evaluation["overall_score"] = overall_score

            print(f"虚拟试穿结果评估完成，总体评分: {overall_score}/10")
            return evaluation
        except Exception as e:
            print(f"评估虚拟试穿结果时出错: {e}")
            return {"error": str(e)}

    def refine_try_on_result(self, try_on_result: Dict, feedback: str) -> Dict:
        """根据反馈优化虚拟试穿结果"""
        try:
            # 检查必要的数据
            if not try_on_result.get("success", False) or "result_image" not in try_on_result:
                print(f"优化失败: 输入的试穿结果无效")
                return {"success": False, "error": "输入的试穿结果无效"}

            # 提取必要的信息
            result_image_path = try_on_result["result_image"]
            person_image_path = self._get_person_image_from_result(try_on_result)
            clothing_image_path = self._get_clothing_image_from_result(try_on_result)
            clothing_description = self._get_clothing_description_from_result(try_on_result)

            # 检查这些文件是否存在
            if not person_image_path or not os.path.exists(person_image_path):
                print(f"优化失败: 找不到人物图像")
                return {"success": False, "error": "找不到人物图像"}
            
            if not clothing_image_path or not os.path.exists(clothing_image_path):
                print(f"优化失败: 找不到服装图像")
                return {"success": False, "error": "找不到服装图像"}

            # 重新执行虚拟试穿，使用相同的参数但添加反馈
            refined_result = self.try_on_clothing(
                person_image_path=person_image_path,
                clothing_image_path=clothing_image_path,
                clothing_description=clothing_description + f"。用户反馈: {feedback}",
                iterations=try_on_result.get("iterations", MAX_FLUX_VTON_ITERATIONS),
                guidance_scale=try_on_result.get("guidance_scale", VTON_GUIDANCE_SCALE)
            )

            if refined_result.get("success", False):
                print(f"根据反馈优化虚拟试穿结果成功")
                # 将原始结果和优化结果一起返回，便于比较
                return {
                    "success": True,
                    "original_result": try_on_result,
                    "refined_result": refined_result,
                    "feedback": feedback
                }
            else:
                print(f"根据反馈优化虚拟试穿结果失败")
                return refined_result
        except Exception as e:
            print(f"优化虚拟试穿结果时出错: {e}")
            return {"success": False, "error": str(e)}

    def batch_try_on(self, person_image_path: str, clothing_image_paths: List[str], 
                    clothing_descriptions: List[str] = None) -> List[Dict]:
        """批量执行虚拟试穿"""
        try:
            results = []

            # 如果没有提供描述，则使用空描述
            if clothing_descriptions is None:
                clothing_descriptions = [""] * len(clothing_image_paths)
            else:
                # 确保描述列表长度与图像列表匹配
                if len(clothing_descriptions) < len(clothing_image_paths):
                    clothing_descriptions += [""] * (len(clothing_image_paths) - len(clothing_descriptions))

            # 对每件服装执行虚拟试穿
            for i, (clothing_image_path, clothing_description) in enumerate(zip(clothing_image_paths, clothing_descriptions)):
                print(f"批量试穿: 处理第 {i+1}/{len(clothing_image_paths)} 件服装")
                result = self.try_on_clothing(
                    person_image_path=person_image_path,
                    clothing_image_path=clothing_image_path,
                    clothing_description=clothing_description
                )
                results.append(result)

            print(f"批量虚拟试穿完成，共处理 {len(results)} 件服装")
            return results
        except Exception as e:
            print(f"批量执行虚拟试穿时出错: {e}")
            return []

    def compare_try_on_results(self, results: List[Dict]) -> Dict:
        """比较多个虚拟试穿结果"""
        try:
            # 筛选成功的结果
            successful_results = [r for r in results if r.get("success", False)]

            if not successful_results:
                print(f"比较失败: 没有成功的试穿结果")
                return {"error": "没有成功的试穿结果"}

            # 计算每个结果的总体评分
            scored_results = []
            for result in successful_results:
                # 获取CLIP评分
                if "clip_scores" in result and result["clip_scores"]:
                    clip_scores = result["clip_scores"]
                    avg_clip_score = sum(clip_scores) / len(clip_scores) if clip_scores else 0
                else:
                    avg_clip_score = 0

                scored_results.append({
                    "result": result,
                    "score": avg_clip_score
                })

            # 按评分排序
            scored_results.sort(key=lambda x: x["score"], reverse=True)

            # 构建比较结果
            comparison = {
                "total_results": len(results),
                "successful_results": len(successful_results),
                "sorted_results": [sr["result"] for sr in scored_results],
                "best_result": scored_results[0]["result"] if scored_results else None,
                "worst_result": scored_results[-1]["result"] if scored_results else None
            }

            print(f"比较虚拟试穿结果完成，成功比较了 {len(successful_results)} 个结果")
            return comparison
        except Exception as e:
            print(f"比较虚拟试穿结果时出错: {e}")
            return {"error": str(e)}

    def save_try_on_result(self, try_on_result: Dict, output_folder: str) -> Dict:
        """保存虚拟试穿结果"""
        try:
            # 检查结果是否有效
            if not try_on_result.get("success", False) or "result_image" not in try_on_result:
                print(f"保存失败: 输入的试穿结果无效")
                return {"success": False, "error": "输入的试穿结果无效"}

            # 确保输出目录存在
            os.makedirs(output_folder, exist_ok=True)

            # 保存结果图像
            result_image = Image.open(try_on_result["result_image"])
            result_image_path = os.path.join(output_folder, "final_result.png")
            result_image.save(result_image_path)

            # 保存迭代结果
            iteration_folder = os.path.join(output_folder, "iterations")
            os.makedirs(iteration_folder, exist_ok=True)
            
            if "iteration_results" in try_on_result:
                for i, iteration_image_path in enumerate(try_on_result["iteration_results"]):
                    iteration_image = Image.open(iteration_image_path)
                    iteration_image.save(os.path.join(iteration_folder, f"iteration_{i+1}.png"))

            # 保存元数据
            metadata = {
                "success": try_on_result["success"],
                "best_iteration": try_on_result.get("best_iteration", 0),
                "clip_scores": try_on_result.get("clip_scores", []),
                "timestamp": str(np.datetime64('now'))
            }
            
            metadata_path = os.path.join(output_folder, "metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)

            print(f"虚拟试穿结果已保存到: {output_folder}")
            return {
                "success": True,
                "result_image_path": result_image_path,
                "iteration_folder": iteration_folder,
                "metadata_path": metadata_path
            }
        except Exception as e:
            print(f"保存虚拟试穿结果时出错: {e}")
            return {"success": False, "error": str(e)}

    # 辅助方法
    def _get_person_image_from_result(self, try_on_result: Dict) -> Optional[str]:
        """从试穿结果中提取人物图像路径"""
        # 这是一个辅助方法，实际应用中可能需要根据具体情况实现
        # 例如，可以从try_on_result中存储的元数据获取
        return None

    def _get_clothing_image_from_result(self, try_on_result: Dict) -> Optional[str]:
        """从试穿结果中提取服装图像路径"""
        # 这是一个辅助方法，实际应用中可能需要根据具体情况实现
        # 例如，可以从try_on_result中存储的元数据获取
        return None

    def _get_clothing_description_from_result(self, try_on_result: Dict) -> str:
        """从试穿结果中提取服装描述"""
        # 这是一个辅助方法，实际应用中可能需要根据具体情况实现
        # 例如，可以从try_on_result中存储的元数据获取
        return ""