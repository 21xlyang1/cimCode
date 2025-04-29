from flask import Blueprint, jsonify,session
from flask import request,g

from models import Organization, Admin, Resident, Camera, ActivationCode, OperationRecord,RTSP
from datetime import datetime
from exts import db
from werkzeug.security import generate_password_hash, check_password_hash
# from decorators import login_required

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/')
def index():
    pass


@bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        data_json = request.get_json()
        if "data" in data_json:
            # 当前时间
            isSuccess = False
            current_time = datetime.now()
            # 格式化为字符串
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            data_json = data_json["data"]

            username = data_json.get('username')
            password = data_json.get('password')
            # repassword = data_json.get('repassword')
            realName = data_json.get('realName')
            phoneNumber = data_json.get('phoneNumber')
            # organizationId = data_json.get('organizationId')
            activationCode = data_json.get('activationCode')
            powerLevel = 2
            createTime = current_time.strftime("%Y-%m-%d %H:%M:%S")
            updateTime = current_time.strftime("%Y-%m-%d %H:%M:%S")
            deleteTime = None

            if not all([username, password, realName, phoneNumber,  activationCode]):
                return jsonify(msg='参数不完整', isSuccess=False)
            if is_activation_code_available(activationCode):
                print(1)
                activation_code = ActivationCode.query.filter_by(activationCode=activationCode, isUsed=False).first()
                organizationId = activation_code.organizationId
            else:
                return jsonify(msg='激活码不存在或已被激活', isSuccess=False)
            user = Admin(username=username, password=generate_password_hash(password), realName=realName, phoneNumber=phoneNumber,
                         organizationId=organizationId, activationCode=activationCode, powerLevel=powerLevel,
                         createTime=createTime, updateTime=updateTime, deleteTime=deleteTime)
            db.session.add(user)
            db.session.commit()
            mark_activation_code_used(activationCode)
            return jsonify(msg='success', isSuccess=True)
        else:
            return jsonify(msg="Data not found")
    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)


# 添加激活码###############################################################
@bp.route('/activation_code', methods=['POST'])
def activation_code():
    try:
        data_json = request.get_json()
        if "data" in data_json:
            data_json = data_json["data"]
            # activation_code=data_json.get('activation_code')
            organizationId = data_json.get('organizationId')
            activationCode = data_json.get('activationCode')
            isUsed = False
            if not activationCode:
                return jsonify(msg='参数不完整', isSuccess=False)
            act = ActivationCode(organizationId=organizationId, activationCode=activationCode, isUsed=isUsed)
            db.session.add(act)
            db.session.commit()
            return jsonify(msg='success', isSuccess=True)
        else:
            return jsonify(msg="Data not found")
    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)


# 添加组织
@bp.route('/Organization', methods=['POST'])
def C_Organization():
    try:
        data_json = request.get_json()
        if "data" in data_json:
            data_json = data_json["data"]
            organizationName = data_json.get('organizationName')
            # print(organizationName)
            # print(type(organizationName))
            createTime = datetime.now()
            updateTime = datetime.now()
            deleteTime = None
            organization = Organization(organizationName=organizationName, createTime=createTime, updateTime=updateTime,
                                        deleteTime=deleteTime)
            db.session.add(organization)
            db.session.commit()
            return jsonify(msg='success', isSuccess=True)
        else:
            return jsonify(msg="Data not found")
    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)


@bp.route('/test', methods=['GET'])
def test():
    return "test"

#登录api
@bp.route('/login', methods=['POST'])
def login():
    try:
        data_json = request.get_json()
        if "data" in data_json:
            data_json = data_json["data"]
            username = data_json.get('username')
            password = data_json.get('password')
            if not all([username, password]):
                return jsonify(msg='参数不完整', isSuccess=False)
            user = Admin.query.filter_by(username=username).first()
            if user:
                if check_password_hash(user.password, password):
                    # session['user_id'] = user.userId
                    return jsonify(data={"userId":user.userId}, msg='success', isSuccess=True)
                else:
                    return jsonify(msg='密码错误', isSuccess=False)
            else:
                return jsonify(msg='用户不存在', isSuccess=False)
        else:
            return jsonify(msg="Data not found")
    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)


#退出
@bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return jsonify(msg='success', isSuccess=True)

#添加常住人口数据
@bp.route('/addresident', methods=['POST'])
# @login_required
def addresident():
    try:
        data_json = request.get_json()
        if "data" in data_json:
            data_json = data_json["data"]
            nativename=data_json.get('nativename')
            phoneNumber=data_json.get('phoneNumber')
            address=data_json.get('address')
            birthday=data_json.get('birthday')
            sex=data_json.get("sex")
            userId = data_json.get('userId')
            # Query the Admin from the database
            admin = Admin.query.filter_by(userId=userId).first()
            if not admin:
                return jsonify(msg='Admin not found', isSuccess=False)
            # Get the organizationId from the Admin
            organizationId = admin.organizationId
            createTime=datetime.now()
            updateTime=datetime.now()
            deleteTime=None
            if not all([nativename,phoneNumber,address,birthday,sex,organizationId,createTime,updateTime,userId]):
                return jsonify(msg='参数不完整', isSuccess=False)
            resident = Resident(nativename=nativename,phoneNumber=phoneNumber,address=address,birthday=birthday,sex=sex,organizationId=organizationId,createTime=createTime,updateTime=updateTime,deleteTime=deleteTime)
            db.session.add(resident)
            db.session.commit()
            resident = Resident.query.filter_by(nativename=nativename,phoneNumber=phoneNumber,address=address).first()
            recordType ="添加常住人口"
            nativeId =resident.nativeId
            time =datetime.now()
            opera=OperationRecord(userId=userId,recordType=recordType,nativeId=nativeId,time=time)
            db.session.add(opera)
            db.session.commit()
            return jsonify(msg='success', isSuccess=True)
        else:
            return jsonify(msg="Data not found")
    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)



#删除常住人口数据
@bp.route('/deleteresident', methods=['POST'])
# @login_required
def deleteresident():
    try:
        data_json = request.get_json()
        if "data" in data_json:
            data_json = data_json["data"]
            nativeId=data_json.get('nativeId')
            userId = data_json.get('userId')
            deleteTime=datetime.now()
            if not all([nativeId,deleteTime,userId]):
                return jsonify(msg='参数不完整', isSuccess=False)
            resident = Resident.query.filter_by(nativeId=nativeId).first()
            resident.deleteTime=deleteTime
            db.session.commit()
            recordType ="删除常住人口"
            time =datetime.now()
            opera=OperationRecord(userId=userId,recordType=recordType,nativeId=nativeId,time=time)
            db.session.add(opera)
            db.session.commit()
            return jsonify(msg='success', isSuccess=True)
        else:
            return jsonify(msg="Data not found")

    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)

#查询常住人口数据
@bp.route('/searchresident', methods=['POST'])
# @login_required
def searchresident():
    try:
        data_json = request.get_json()
        if "data" in data_json:
            data_json = data_json["data"]
            nativeId=data_json.get('nativeId')
            if not all([nativeId]):
                return jsonify(msg='参数不完整', isSuccess=False)
            resident = Resident.query.filter_by(nativeId=nativeId).first()
            resident_data = {
                'nativeId': resident.nativeId,
                'guardianId': resident.guardianId,
                'nativename': resident.nativename,
                'phoneNumber': resident.phoneNumber,
                'address': resident.address,
                'birthday': resident.birthday.isoformat() if resident.birthday else None,
                'sex': resident.sex,
                'organizationId': resident.organizationId,
                'createTime': resident.createTime.isoformat() if resident.createTime else None,
                'updateTime': resident.updateTime.isoformat() if resident.updateTime else None,
                'deleteTime': resident.deleteTime.isoformat() if resident.deleteTime else None,
            }
            return jsonify(msg='success', isSuccess=True, data=resident_data)
        else:
            return jsonify(msg="Data not found")

    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)

#展示所有常住人口数据
@bp.route('/showresident', methods=['POST'])
# @login_required
def showresident():
    try:
        residents = Resident.query.filter(Resident.deleteTime == None).all()
        resident_data = []
        for resident in residents:
            resident_item = {
                'nativeId': resident.nativeId,
                'guardianId': resident.guardianId,
                'nativename': resident.nativename,
                'phoneNumber': resident.phoneNumber,
                'address': resident.address,
                'birthday': resident.birthday.isoformat() if resident.birthday else None,
                'sex': resident.sex,
                'organizationId': resident.organizationId,
                'createTime': resident.createTime.isoformat() if resident.createTime else None,
                'updateTime': resident.updateTime.isoformat() if resident.updateTime else None,
                'deleteTime': resident.deleteTime.isoformat() if resident.deleteTime else None,
            }
            resident_data.append(resident_item)

        return jsonify(data=resident_data, msg='success', isSuccess=True)

    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)



#查看操作记录表
@bp.route('/showoperationrecord', methods=['GET'])
# @login_required
def showoperationrecord():
    try:
        operationrecords = OperationRecord.query.all()
        operationrecord_data = []
        for operationrecord in operationrecords:
            operationrecord_item = {
                'recordId': operationrecord.recordId,
                'userId': operationrecord.userId,
                'recordType': operationrecord.recordType,
                'nativeId': operationrecord.nativeId,
                'time': operationrecord.time.isoformat() if operationrecord.time else None,
            }
            operationrecord_data.append(operationrecord_item)

        return jsonify(data=operationrecord_data, msg='success', isSuccess=True)

    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)






#添加常住人口数据################测试用的##############
@bp.route('/addresidentceshi', methods=['POST','GET'])
# @login_required
def addresidentceshi():
    try:
        nativename='nativename'
        phoneNumber='phoneNumber'
        address='address'
        birthday='2014-03-11'
        sex="sex"
        organizationId=1
        createTime=datetime.now()
        updateTime=datetime.now()
        deleteTime=None
        if not all([nativename,phoneNumber,address,birthday,sex,organizationId,createTime,updateTime]):
            return jsonify(msg='参数不完整', isSuccess=False)
        resident = Resident(nativename=nativename,phoneNumber=phoneNumber,address=address,birthday=birthday,sex=sex,organizationId=organizationId,createTime=createTime,updateTime=updateTime,deleteTime=deleteTime)
        db.session.add(resident)
        db.session.commit()
        resident = Resident.query.filter_by(nativename=nativename,phoneNumber=phoneNumber,address=address).first()
        userId =g.user.userId
        recordType ="添加常住人口"
        nativeId =resident.nativeId
        time =datetime.now()
        opera=OperationRecord(userId=userId,recordType=recordType,nativeId=nativeId,time=time)
        db.session.add(opera)
        db.session.commit()
        return jsonify(msg='success', isSuccess=True)
    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)



#添加临时人口数据

@bp.route('/lingshi', methods=['POST', 'GET'])
def lingshi():
    try:
        # data_json = request.get_json()
        # if "data" in data_json:
        #     data_json = data_json["data"]
            username = "ceshi"
            password = 'password'
            if not all([username, password]):
                return jsonify(msg='参数不完整', isSuccess=False)
            user = Admin.query.filter_by(username=username).first()
            if user:
                if check_password_hash(user.password, password):
                    session['user_id'] = user.userId
                    return jsonify(msg='success', isSuccess=True)
                else:
                    return jsonify(msg='密码错误', isSuccess=False)
            else:
                return jsonify(msg='用户不存在', isSuccess=False)
    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)

#得到rtsp
@bp.route('/getcameratrsp', methods=['POST'])
def get_camera_rtsp():
    try:
        data_json = request.get_json()

        if not data_json or "data" not in data_json:
            return jsonify(msg="Data not found", isSuccess=False)

        data_json = data_json["data"]
        camera_id = data_json.get('cameraId')

        if not camera_id:
            return jsonify(msg='参数不完整', isSuccess=False)

        camera = RTSP.query.filter_by(rtspId=camera_id).first()

        if not camera:
            return jsonify(msg='摄像头不存在', isSuccess=False)

        return jsonify(isSuccess=True, msg='success', data=[{"cameraRTSP": camera.rtsp_url}])

    except Exception as e:
        print(e)
        return jsonify(msg='error', isSuccess=False)











# 各种函数：
# 判断是否存在相同且未使用的激活码 "123456"
def is_activation_code_available(code):
    activation_code = ActivationCode.query.filter_by(activationCode=code, isUsed=False).first()
    return activation_code is not None


# 将未使用过的激活码 "123456" 设置为已使用
def mark_activation_code_used(code):
    activation_code = ActivationCode.query.filter_by(activationCode=code, isUsed=False).first()
    if activation_code:
        activation_code.isUsed = True
        db.session.commit()
