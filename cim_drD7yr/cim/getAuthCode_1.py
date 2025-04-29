import requests
import random
import string
import time
import xxtea
import hmac
import json
from hashlib import sha256

# 账号 13923998829
# 密码 202020Aa@

# 接口URL
url = "https://vcp.21cn.com/open/oauth/login/getAuthPageUrl"

appId = "693299085757"
appSecret = "88bd97ee5e9949c2bc48efb6e6fa2207"
CLIENT_TYPE = 3
VERSION = "v2.0"

# callbackUrl = "http://192.168.100.30:8888"

callbackUrl = "http://192.168.140.1:8889"

loginClientType = 10010


def public_params(params):
    """ 共有请求参数 """
    timestamp = int(time.time() * 1000)
    return {"signature": get_sign(params, timestamp), "params": params, "appId": appId,
                'version': VERSION,  "clientType": CLIENT_TYPE, "timestamp": timestamp}

def get_sign(params, timestamp):
    """ 获取签名 """
    data = appId+str(CLIENT_TYPE)+str(params)+str(timestamp)+VERSION
    # print(data)
    return hmac.new(appSecret.encode('utf-8'), data.encode('utf-8'), digestmod=sha256).hexdigest()

def generate_state(length=16):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


def send_post(paramDict):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "accept": "*/*",
        "connection": "Keep-Alive",
        "user-agent": "ehome-push"
    }
    # print("请求头参数 %s" % headers)
    # 发送POST请求`
    response = requests.post(url, paramDict, headers)
    # print(response)
    return response



def main():

    state = generate_state()
    reqParam = "callbackUrl=%s&state=%s&loginClientType=10010" % (callbackUrl, state)

    param = xxtea.encrypt(reqParam, appSecret).hex()
    realParam = public_params(param)
    result = send_post(realParam)
    # print("请求体参数:%s" % realParam )

    print("result.content=%s" % (result.content).decode('utf-8'))
    value = json.loads(result.text)
    print(value)


if __name__ == '__main__':
    main()