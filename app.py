from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from embedchain import App
import os
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler("./chatbot.log", maxBytes=10000, backupCount=1)
handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)


app = Flask(__name__)
app.logger.addHandler(handler)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class TrackedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), unique=True, nullable=False)
with app.app_context():
    db.create_all()

gpt_app = App.from_config(config_path="openai.yaml")


@app.route('/')
def index():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    logger.info(f"User input: {user_input}")
    try:
        if user_input == "#update":
            check_and_update_files()
            response = "Files updated successfully!"
        else:
            response = gpt_app.query(user_input)
            logger.info(f"Chatbot response: {response}")
    except:
        logger.error("OpenAI API error", exc_info=True)
        response = "Sorry, I can't get response from OpenAI. Please try again later."
    return jsonify({"response": response})

def check_and_update_files():
    existing_files = {file.filename for file in TrackedFile.query.all()}
    current_files = set(os.listdir('document'))
    new_files = current_files - existing_files
    deleted_files = existing_files - current_files  # 被删除的文件集合

    # 添加新文件
    for file_name in new_files:
        logger.info(f"New file detected: {file_name}")
        file_path = os.path.join('document', file_name)
        if file_path.endswith('.pdf'):
            gpt_app.add(file_path, data_type='pdf_file')
        elif file_path.endswith('.txt'):
            gpt_app.add(file_path)
        else:
            logger.info(f"Unsupported file type: {file_name}")
            continue
        db.session.add(TrackedFile(filename=file_name))
    
    # 处理被删除的文件
    if deleted_files:
        metadatas = gpt_app.db.get()  # 获取所有文件的元数据
        for deleted_file in deleted_files:
            # 从元数据中找到被删除文件的hash值
            for metadata in metadatas.get('metadatas', []):
                if metadata['url'].endswith(deleted_file):  # 假设url字段包含文件名
                    gpt_app.delete(metadata['hash'])  # 删除对应的文件信息
                logger.info(f"Deleted file info: {deleted_file}")
            # 从数据库中移除
            TrackedFile.query.filter_by(filename=deleted_file).delete()
    
    db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)
