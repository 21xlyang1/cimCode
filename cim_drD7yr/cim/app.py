# -*- coding: utf-8 -*-

from flask import Flask
import config
from exts import db
#蓝图
from blueprints.auth import bp as auth_bp
from blueprints.other import bp as other_bp
from flask_migrate import Migrate
from flask_cors import CORS
from getDeviceRtsp import everytime_rtsp_run
from websocket.app import webrun
import threading

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

migrate=Migrate(app,db)

#产生关联
app.register_blueprint(auth_bp)
app.register_blueprint(other_bp)

#跨域
CORS(app)

# #钩子函数
# @app.before_request
# def before_request():
#     user_id=session.get('user_id')
#     if user_id:
#         user=Admin.query.get(user_id)
#         setattr(g,'user',user)
#     else:
#         setattr(g,'user',None)
#
# @app.context_processor
# def my_context_processor():
#     return {'user':g.user}




if __name__ == '__main__':
    # everytime_rtsp_run_thread = threading.Thread(target=everytime_rtsp_run)
    # everytime_rtsp_run_thread.start()
    #
    # # 创建另一个线程来运行 webrun 函数
    # webrun_thread = threading.Thread(target=webrun)
    # webrun_thread.start()

    # 在主线程中运行 app.run() 函数
    app.run(host='0.0.0.0', port=5000)
