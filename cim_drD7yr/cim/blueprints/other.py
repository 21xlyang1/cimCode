from flask import Blueprint, jsonify,session
from flask import request,g

from models import Organization, Admin, Resident, Camera, ActivationCode, OperationRecord,RTSP
from datetime import datetime
from exts import db
from werkzeug.security import generate_password_hash, check_password_hash

bp=Blueprint('other', __name__, url_prefix='/')

@bp.route('/')
def index():
    return "hello worId"

# @bp.route('/camera/getAllInf', methods=['POST'])
# def get_all_cameras_info():
#     all_cameras = Camera.query.all()
#     data = []
#     for camera in all_cameras:
#         data.append({'data':{
#             'cameraId': camera.cameraId,
#             'address': camera.place,
#             "latitude": camera.latitude,
#             'longitude': camera.longitude,
#             'organizationId': camera.organizationId,
#             'place': camera.place
#         }})
#     print(data)
#     return jsonify(data)
@bp.route('/camera/getAllInf', methods=['POST'])
def get_all_cameras_info():
    all_cameras = RTSP.query.all()
    data = []
    for camera in all_cameras:
        data.append({'data':{
            'cameraId': camera.rtspId,
            'address': camera.deviceCode,
            "latitude": camera.latitude,
            'longitude': camera.longitude,
            'organizationId': "1",
            'place': camera.deviceName
        }})
    print(data)
    return jsonify(data)
