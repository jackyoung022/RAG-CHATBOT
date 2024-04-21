# 基于RAG技术的QA机器人
## 项目介绍
该项目主要是通过OpenAI的的语言对话功能并结合RAG技术，实现文本检索、对话功能。

## 项目实现
该项目基于[embedchain框架](https://github.com/embedchain/embedchain)实现。

## OpenAI API Key
在openai.yaml文件中更改OpenAI的api_key为自己的Key

## 开发部署
```bash
pip install -r requirements.txt
python app.py
```

## Docker 部署
```bash
docker build -t chatbot-nsfocus .
docker run -d --name chatbot-nsfocus -p 55580:5000 -v $(pwd):/app chatbot-nsfocus
```

## Docker Compose 部署
```bash
docker compose up -d
```

## 添加文章输入
目前只支持txt和pdf的文件类型，其他文件类型还没有测试。只用将文件上传到`document`目录中，在前端输入'#update'既可完成文档更新