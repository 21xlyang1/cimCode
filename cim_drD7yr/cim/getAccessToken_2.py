import requests
import time
import xxtea
import hmac
import json
from hashlib import sha256


# 接口URL
url = "https://vcp.21cn.com/open/oauth/getAccessToken"

appId = "693299085757"
appSecret = "88bd97ee5e9949c2bc48efb6e6fa2207"
CLIENT_TYPE = "3"
VERSION = "v2.0"

grantType = "auth_code"
authCode = "VwsI4Fl95uEauhCdSCUojtXb"  # 需要更新
refeshToken = ""
apiVersion = "2.0"

def public_params(params):
    """ 共有请求参数 """
    timestamp = int(time.time() * 1000)
    return {"signature": get_sign(params, timestamp), "params": params, "appId": appId,
                'version': VERSION,  "clientType": CLIENT_TYPE, "timestamp": timestamp}

def get_sign(params, timestamp):
    """ 获取签名 """
    data = appId+CLIENT_TYPE+str(params)+str(timestamp)+VERSION
    # print(data)
    return hmac.new(appSecret.encode('utf-8'), data.encode('utf-8'), digestmod=sha256).hexdigest()



def send_post(paramDict):
    headers = {
        "apiVersion": "2.0",   # 返回结果出现70012错误码时加上这行
        "Content-Type": "application/x-www-form-urlencoded",
        "accept": "*/*",
        "connection": "Keep-Alive",
        "user-agent": "ehome-push"
    }
    # print("请求头参数 %s" % headers)
    # 发送POST请求`
    response = requests.post(url, paramDict, headers=headers)
    # print(response)
    return response



def main():

    reqParam = "grantType=%s&authCode=%s&refeshToken=%s" % (grantType, authCode, refeshToken)

    # reqParam = "grantType=%s&apiVersion=2.0" % (grantType)
    # reqParam = "grantType=%s&authCode=%s&refeshToken=%s&apiVersion=%s" % (grantType, authCode, refeshToken, "2.0")

    param = xxtea.encrypt(reqParam, appSecret).hex()
    realParam = public_params(param)
    result = send_post(realParam)
    # print("请求体参数:%s" % realParam )

    print("result.content=%s" % (result.content).decode('utf-8'))
    value = json.loads(result.text)
    print(value)
    # 将数据写入 JSON 文件
    with open('data.json', 'w') as json_file:
        json.dump(value, json_file, indent=4)

if __name__ == '__main__':
    main()