# 使用官方Python镜像作为基础镜像
FROM python:3.10-slim

# 设置工作目录为/app
WORKDIR /app

# 将当前目录下的所有文件复制到容器的/app目录
COPY . /app

# 安装所有依赖
RUN pip install --no-cache-dir -r requirements.txt

# 声明容器内部监听的端口号
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 启动Flask应用
CMD ["flask", "run"]