import binascii
import json
import requests
import xxtea
import time
import hmac
import datetime
from hashlib import sha256

api_rtsp_url = "https://vcp.21cn.com/open/token/cloud/getDeviceMediaUrlRtsp"
api_device_url = "https://vcp.21cn.com/open/token/vcpTree/getDevicesByRegionCon"

# 请求参数值
appId = "693299085757"
appSecret = "88bd97ee5e9949c2bc48efb6e6fa2207"
CLIENT_TYPE = "3"
VERSION = "v2.0"

# accessToken有效时长24小时
accessToken = "ygwVdCACTux2OTTrZp6gS7mCNuQ0o3gT"

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


        # print("设备名称:%s   设备码: %s  流地址: %s" % (deviceName, deviceCode, hlsUrl['url']))
        data_json.append({
            'deviceName': deviceName,
            'deviceCode': deviceCode,
            'deviceRtsp': hlsUrl
        })
        return
    else:
        print("请求失败")

def run():
    cur_time = datetime.datetime.now()
    deviceNameCode = getDevice()
    # print(deviceNameCode)

    for device_name, device_code in deviceNameCode.items():
        getRtsp(device_name, device_code)
        # time.sleep(0.1)
    print("总耗时：%s" % (datetime.datetime.now()-cur_time))
    # json格式转换
    result = {'data': data_json}
    json_result = json.dumps(result, ensure_ascii=False, indent=4)
    print(json_result)

if __name__ == '__main__':
    run()
    # print(xxtea)
