from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Rtsp(db.Model):
    __tablename__ = 'rtsp'
    rtspId = db.Column(db.Integer, primary_key=True)
    deviceCode = db.Column(db.String(255))
    deviceName = db.Column(db.String(255))
    rtsp_url = db.Column(db.String(255))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    time = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Rtsp {self.rtsp_url}>'
