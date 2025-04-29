from flask import Flask
from videoCapture.flask_app.config import Config
from models import db, Rtsp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


def create_tables():
    with app.app_context():
        db.create_all()


def get_rtsp_url_by_id(rtsp_id):
    with app.app_context():
        rtsp_entry = Rtsp.query.filter_by(rtspId=rtsp_id).first()
        if rtsp_entry:
            return rtsp_entry.rtsp_url
        else:
            return None


if __name__ == '__main__':
    # create_tables()

    # 示例：查询 ID 为 23 的 rtsp_url
    rtsp_url = get_rtsp_url_by_id(18)
    print(f"RTSP URL for ID 18: {rtsp_url}")

    app.run(debug=True)
