# PersonalStyleAgent - 个人风格服装生成与虚拟试穿系统

PersonalStyleAgent 是一个基于人工智能的个人风格服装生成与虚拟试穿系统，能够根据用户的风格需求生成定制的服装图像，并提供虚拟试穿体验。

## 功能特点

1. **风格需求分析**：通过自然语言处理，理解用户的服装风格需求
2. **服装图像生成**：基于风格需求生成高质量的服装图像
3. **虚拟试穿**：将生成的服装图像与用户照片进行虚拟试穿
4. **试穿效果优化**：根据用户反馈优化虚拟试穿效果
5. **服装推荐**：基于用户风格提供相关服装商品推荐
6. **完整的用户界面**：提供直观易用的Gradio界面

## 技术栈

- **核心框架**：Python、PyTorch、Gradio
- **大语言模型**：Qwen2.5系列模型（用于自然语言处理）
- **图像处理**：PIL、OpenCV、diffusers、transformers
- **搜索功能**：DuckDuckGo Search
- **工具集成**：LangChain

## 项目结构

```
PersonalStyleAgent/
├── agents/                 # Agent模块，包含主要业务逻辑
│   ├── __init__.py         # 模块初始化
│   ├── style_agent.py      # 风格Agent，负责整体协调
│   ├── clothing_recommendation_agent.py  # 服装推荐Agent
│   └── virtual_try_on_agent.py  # 虚拟试穿Agent
├── config/                 # 配置文件
│   └── config.py           # 全局配置参数
├── utils/                  # 工具函数库
│   ├── __init__.py         # 模块初始化
│   ├── need2text.py        # 用户需求转服装描述
│   ├── text2garment.py     # 文本描述转服装图像
│   ├── flux_vton.py        # 虚拟试穿核心功能
│   ├── metrics.py          # 评估指标
│   ├── image_process.py    # 图像处理工具
│   ├── search.py           # 商品搜索功能
│   └── human_mask/         # 人体检测与分割模块
├── static/                 # 静态资源目录
├── templates/              # 模板文件目录
├── app.py                  # 应用主入口
└── requirements.txt        # 项目依赖
```

## 安装说明

### 1. 克隆项目

```bash
git clone [项目地址]
cd PersonalStyleAgent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

在 `config/config.py` 文件中配置必要的API密钥：

```python
# 示例配置
OPENAI_API_KEY = "your_openai_api_key"
```

### 4. 运行应用

```bash
python app.py
```

应用将在 http://localhost:7860 启动。

## 使用方法

1. **输入风格需求**：在文本框中描述您的服装风格需求，点击"分析风格需求"按钮
2. **生成服装图像**：设置生成的服装数量，点击"生成服装图像"按钮
3. **选择服装**：在生成的服装图像中点击选择一件喜欢的服装
4. **上传照片**：上传您的照片用于虚拟试穿
5. **虚拟试穿**：点击"虚拟试穿"按钮，查看试穿效果
6. **优化效果**：如果对试穿效果不满意，可以提供反馈并点击"优化试穿结果"按钮
7. **获取推荐**：输入推荐风格和数量，点击"获取服装推荐"按钮

## 配置说明

在 `config/config.py` 文件中可以配置以下参数：

- `OPENAI_API_KEY`：OpenAI API密钥
- `MODEL_CONFIG`：模型配置参数
- `VTON_GUIDANCE_SCALE`：虚拟试穿引导比例
- `MAX_FLUX_VTON_ITERATIONS`：虚拟试穿最大迭代次数
- `STATIC_FOLDER`：静态资源文件夹路径
- `OUTPUT_FOLDER`：输出文件文件夹路径

## 注意事项

1. 虚拟试穿功能需要较高的计算资源，可能需要等待较长时间
2. 生成的服装图像质量取决于输入的风格描述详细程度
3. 请确保上传的人物照片清晰，能够清楚看到穿着效果
4. 推荐功能依赖于在线搜索结果，可能会受到网络环境影响

## 许可证

[MIT License](LICENSE)

## 更新日志

### v1.0.0 (2023-xx-xx)
- 首次发布
- 实现风格需求分析、服装图像生成、虚拟试穿、推荐等核心功能
- 提供完整的Gradio用户界面