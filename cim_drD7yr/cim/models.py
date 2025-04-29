from exts import db
from datetime import datetime


# class UserModel(db.Model):
#     __tablename__ = 'user'
#     id=db.Column(db.Integer,primary_key=True,autoincrement=True)
#     username=db.Column(db.String(50),nullable=False)
#     password=db.Column(db.String(50),nullable=False)
#     # email=db.Column(db.String(50),nullable=False,unique=True)
#     join_time=db.Column(db.DateTime,nullable=False,default=datetime.now)

#ORM模型映射成表的三步
#1.flask db init:这步只需要执行一次
#2.flask db migrate：识别ORM模型的改变，生成迁移脚本
#3.flask db upgrade:运行迁移脚本，同步到数据库中



#####################################################
# 组织表
class Organization(db.Model):
    __tablename__ = 'organization'
    organizationId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    organizationName = db.Column(db.String(50), nullable=False)
    createTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updateTime = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    deleteTime = db.Column(db.DateTime)

# 管理员信息表
class Admin(db.Model):
    __tablename__ = 'admin'
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    realName = db.Column(db.String(50))
    phoneNumber = db.Column(db.String(20))
    organizationId = db.Column(db.Integer, db.ForeignKey('organization.organizationId'), nullable=False)
    activationCode = db.Column(db.String(50))
    powerLevel = db.Column(db.Integer)
    createTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updateTime = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    deleteTime = db.Column(db.DateTime)
    # 添加常驻人员外键
    organization = db.relationship('Organization', backref='admins')

# 常驻人员表
class Resident(db.Model):
    __tablename__ = 'resident'
    nativeId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    guardianId= db.Column(db.Integer)
    nativename = db.Column(db.String(50))
    phoneNumber = db.Column(db.String(20))
    address = db.Column(db.String(100))
    birthday = db.Column(db.Date)
    sex = db.Column(db.String(10))
    organizationId = db.Column(db.Integer, db.ForeignKey('organization.organizationId'), nullable=False)
    createTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updateTime = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    deleteTime = db.Column(db.DateTime)
    # 添加摄像头外键
    organization = db.relationship('Organization', backref='residents')

# 摄像头表
class Camera(db.Model):
    __tablename__ = 'camera'
    cameraId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Float)  # 纬度
    longitude = db.Column(db.Float)  # 经度
    organizationId = db.Column(db.Integer, db.ForeignKey('organization.organizationId'), nullable=False)
    place = db.Column(db.String(100))
    organization = db.relationship('Organization', backref='cameras')

# 激活码表
class ActivationCode(db.Model):
    __tablename__ = 'activation_code'
    activationCodeId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    organizationId = db.Column(db.Integer, db.ForeignKey('organization.organizationId'), nullable=False)
    activationCode = db.Column(db.String(50))
    isUsed = db.Column(db.Boolean)
    organization = db.relationship('Organization', backref='activation_codes')

# 操作记录表
class OperationRecord(db.Model):
    __tablename__ = 'operation_record'
    recordId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('admin.userId'), nullable=False)
    recordType = db.Column(db.String(50))
    nativeId = db.Column(db.Integer, db.ForeignKey('resident.nativeId'))
    time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    admin = db.relationship('Admin', backref='operation_records')
    resident = db.relationship('Resident', backref='operation_records')

class RTSP(db.Model):
    __tablename__ = 'rtsp'
    rtspId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deviceCode=db.Column(db.String(50))
    deviceName=db.Column(db.String(50))
    rtsp_url = db.Column(db.String(255))
    longitude=db.Column(db.String(255))
    latitude = db.Column(db.String(255))
    time = db.Column(db.DateTime, nullable=False, default=datetime.now)







