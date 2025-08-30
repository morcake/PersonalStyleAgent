from setuptools import setup, find_packages
import os

# 获取当前目录
here = os.path.abspath(os.path.dirname(__file__))

# 读取README.md文件内容作为项目描述
with open(os.path.join(here, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

# 读取requirements.txt文件内容作为依赖项
with open(os.path.join(here, 'requirements.txt'), 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# 设置项目信息
setup(
    name='PersonalStyleAgent',
    version='1.0.0',
    author='PersonalStyleAgent Team',
    author_email='team@personalstyleagent.example.com',
    description='个人风格服装生成与虚拟试穿系统',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/example/PersonalStyleAgent',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Multimedia :: Graphics',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'personal_style_agent=app:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['templates/*', 'static/*'],
    },
    zip_safe=False
)