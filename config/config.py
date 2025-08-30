import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API配置
API_KEY = os.getenv("API_KEY", "sk-jubcwzentlvmaglywmolelnovhyrgpztuqvlnpcklpjouotz")
BASE_URL = os.getenv("BASE_URL", "https://api.siliconflow.cn/v1")

# Hugging Face 镜像配置
HF_ENDPOINT = os.getenv("HF_ENDPOINT", "https://hf-mirror.com/")
os.environ["HF_ENDPOINT"] = HF_ENDPOINT  # 设置环境变量以使用镜像

# 模型配置
LANGUAGE_MODEL = "Qwen/Qwen2.5-7B-Instruct"
VISION_MODEL = "Pro/Qwen/Qwen2.5-VL-7B-Instruct"

# 路径配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_FOLDER = os.path.join(PROJECT_ROOT, "static")
TEMPLATES_FOLDER = os.path.join(PROJECT_ROOT, "templates")
UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, "uploads")
OUTPUT_FOLDER = os.path.join(STATIC_FOLDER, "outputs")

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 虚拟试穿配置
VTON_GUIDANCE_SCALE = 2.5
VTON_WIDTH = 768
VTON_HEIGHT = 1024
VTON_NUM_IMAGES = 3

# 评分阈值配置
GARMENT_VQA_HIGH_THRESHOLD = {
    "upper_body": 0.75,
    "lower_body": 0.75,
    "dresses": 0.8,
    "shoes": 0.7,
    "hat": 0.7,
    "glasses": 0.7,
    "belt": 0.7,
    "scarf": 0.7
}

GARMENT_VQA_LOW_THRESHOLD = {
    "upper_body": 0.65,
    "lower_body": 0.65,
    "dresses": 0.7,
    "shoes": 0.6,
    "hat": 0.6,
    "glasses": 0.6,
    "belt": 0.6,
    "scarf": 0.6
}

VTON_CLIP_SCORE_HIGH_THRESHOLD = {
    "upper_body": 0.8,
    "lower_body": 0.8,
    "dresses": 0.85,
    "shoes": 0.75,
    "hat": 0.75,
    "glasses": 0.75,
    "belt": 0.75,
    "scarf": 0.75
}

VTON_CLIP_SCORE_LOW_THRESHOLD = {
    "upper_body": 0.7,
    "lower_body": 0.7,
    "dresses": 0.75,
    "shoes": 0.65,
    "hat": 0.65,
    "glasses": 0.65,
    "belt": 0.65,
    "scarf": 0.65
}

# 迭代次数配置
MAX_TEXT2GARMENT_ITERATIONS = 3
MAX_FLUX_VTON_ITERATIONS = 3

# 搜索配置
SEARCH_TIMEOUT = 30  # 搜索超时时间（秒）
SEARCH_RESULT_LIMIT = 50  # 搜索结果限制
IMAGE_DOWNLOAD_TIMEOUT = 15  # 图像下载超时时间（秒）

# 类别配置
CATEGORY_DICT_UTILS = ["upper_body", "lower_body", "dresses", "shoes", "hat", "glasses", "belt", "scarf"]