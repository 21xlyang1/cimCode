import binascii
import json
import requests
import xxtea
import hmac
from hashlib import sha256

import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import RTSP
from datetime import datetime
from refreshToken_3 import updataToken
import schedule
import time

# 使用配置文件中的数据库 URI 创建 engine
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)

api_rtsp_url = "https://vcp.21cn.com/open/token/cloud/getDeviceMediaUrlRtsp"
api_device_url = "https://vcp.21cn.com/open/token/vcpTree/getDevicesByRegionCon"
api_location_url="https://vcp.21cn.com/open/token/vcpTree/getDeviceByDeviceCode"
#https://vcp.dlife.cn/

# 请求参数值
appId = "693299085757"
appSecret = "88bd97ee5e9949c2bc48efb6e6fa2207"
CLIENT_TYPE = "3"
VERSION = "v2.0"

# accessToken有效时长24小时
accessToken = "0z1lgJb4Fa04RnaHwQrgCfN3k3DvHgZv"

# 格式转换的辅助变量
data_json = []

def public_params(params):
    """ 共有请求参数 """
    timestamp = int(time.time() * 1000)
    return {"signature": get_sign(params, timestamp), "params": params, "appId": appId,
                'version': VERSION, "clientType": CLIENT_TYPE, "timestamp": timestamp}

def get_sign(params, timestamp):
    """ 获取签名 """
    data = appId+CLIENT_TYPE+str(params)+str(timestamp)+VERSION
    # print(data)
    return hmac.new(appSecret.encode('utf-8'), data.encode('utf-8'), digestmod=sha256).hexdigest()


def send_post(api_url, paramDict):
    # 构建请求头参数
    headers = {
        "apiVersion": "2.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "accept": "*/*",
        "connection": "Keep-Alive",
        "user-agent": "ehome-push"
    }
    # 发送请求信息
    repsonse = requests.post(api_url, paramDict, headers=headers)

    return repsonse

def getDevice():
    # 存储所有的设备码以及设备名称
    deviceNameCode = {}

    paramDevice = "accessToken=%s&pageNo=1&pageSize=100" % (accessToken)

    encryptParam = xxtea.encrypt(paramDevice, appSecret).hex()
    realDeviceParam = public_params(encryptParam)

    repsonse = send_post(api_device_url, realDeviceParam)
    # print(repsonse)

    deviceValue = json.loads(repsonse.text)
    print("调用第一个接口的返回结果")
    print(deviceValue)

    if deviceValue['code'] == 0:
        # print("请求失败")

        data = deviceValue['data']['deviceList']
        print(data)
        for item in data:
            device_name = item['deviceName']
            device_code = item['deviceCode']
            deviceNameCode[device_name] = device_code
        # print(deviceNameCode)

        return deviceNameCode
    else:
        print("请求失败")

def getRtsp(deviceName, deviceCode):
    paramRtsp = "accessToken=%s&deviceCode=%s&mute=0&proto=1&supportDomain=0&mediaType=0" % (accessToken,deviceCode)
    encryptParam = xxtea.encrypt(paramRtsp, appSecret).hex()
    realRtspParam = public_params(encryptParam)

    repsonse = send_post(api_rtsp_url, realRtspParam)

    value = json.loads(repsonse.text)
    print("第二个接口调用的返回结果：")
    print(value)

    if value['code'] == 0:
        # print("请求失败")

        mediaUrl = xxtea.decrypt_utf8(binascii.a2b_hex(value['data']), appSecret)
        hlsUrl = json.loads(mediaUrl)

        longitude, latitude=getLongitudeLatitude(deviceCode)

        # print("设备名称:%s   设备码: %s  流地址: %s" % (deviceName, deviceCode, hlsUrl['url']))
        data_json.append({
            'deviceName': deviceName,
            'deviceCode': deviceCode,
            'deviceRtsp': hlsUrl,
            'longitude':longitude,
            'latitude':latitude
        })
        # print(len(data_json))
        # print(data_json)
        return
    else:
        print("请求失败")

def getLongitudeLatitude(deviceCode):
    paramRtsp = "accessToken=%s&deviceCode=%s&mute=0&proto=1&supportDomain=0&mediaType=0" % (accessToken,deviceCode)
    encryptParam = xxtea.encrypt(paramRtsp, appSecret).hex()
    realRtspParam = public_params(encryptParam)
    repsonse = send_post(api_location_url, realRtspParam)
    value = json.loads(repsonse.text)
    # print("第三个接口调用的返回结果：")
    # print(value)
    # print(value['data']['longitude'])
    # print(value['data']['latitude'])
    longitude = value['data']['longitude']
    latitude= value['data']['latitude']

    # if value['code'] == 0:
    #     # print("请求失败")
    #
    #     data = xxtea.decrypt_utf8(binascii.a2b_hex(value['data']), appSecret)
    #     print(6666)
    #     print(data)
    #     medialongitude = xxtea.decrypt_utf8(binascii.a2b_hex(data['longitude']), appSecret)
    #     medialatitude = xxtea.decrypt_utf8(binascii.a2b_hex(data['latitude']), appSecret)
    #     longitude = json.loads(medialongitude)
    #     latitude=json.loads(medialatitude)
    return longitude,latitude
    #
    #     return
    # else:
    #     print("请求失败")

def run():
    global data_json
    global accessToken
    # 从 JSON 文件中读取数据
    updataToken()
    with open('data.json', 'r') as json_file:
        data = json.load(json_file)
    accessToken=data["data"]["accessToken"]
    print(accessToken)
    deviceNameCode = getDevice()
    # print(deviceNameCode)
    data_json = []
    # print("fasdf",len(data_json))
    for device_name, device_code in deviceNameCode.items():
        getRtsp(device_name, device_code)
        # print(data_json)

    # json格式转换
    result = {'data': data_json}
    # print("data_json",data_json)
    # print(type(result))
    # print(type(result))
    # print(result['data'])
    # print(result['data'][0]["deviceName"])
    # print(result['data'][0]["deviceRtsp"]['url'])
    print(len(result['data']))
    session = Session()
    try:
        for device in result['data']:
            device_code = device["deviceCode"]
            device_name = device["deviceName"]
            rtsp_url = device["deviceRtsp"]['url']
            longitude=device["longitude"]
            latitude=device["latitude"]

            existing_record = session.query(RTSP).filter_by(deviceCode=device_code).first()
            if existing_record:
                # 如果存在，则更新记录
                existing_record.deviceName = device_name
                existing_record.rtsp_url = rtsp_url
                existing_record.time = datetime.now()
                existing_record.longitude=longitude
                existing_record.latitude=latitude
            else:
                # 如果不存在，则创建新记录
                new_record = RTSP(
                    deviceCode=device_code,
                    deviceName=device_name,
                    rtsp_url=rtsp_url,
                    time=datetime.now(),
                    longitude=longitude,
                    latitude=latitude
                )
                session.add(new_record)

        session.commit()  # 提交变更
    except Exception as e:
        session.rollback()  # 如果出现错误，回滚变更
        print(f"Error: {e}")
    finally:
        session.close()  # 关闭 session

def everytime_rtsp_run():
    schedule.every(1).minutes.do(run)

    while True:
        try:
            # 运行所有可以运行的任务
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            print("发生异常:", str(e))
            continue

if __name__ == '__main__':
    # everytime_rtsp_run()
    while True:
        try:
            run()
        except Exception as e:
            print(f"Error: {e}")
    # while True:
    #     run()
