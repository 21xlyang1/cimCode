import asyncio
import websockets
import json  # 导入json库
def webrun():
    loop = asyncio.new_event_loop()  # 为这个线程创建一个新的事件循环
    asyncio.set_event_loop(loop)
    async def echo(websocket, path):
        # 只接受 '/ceshi' 路径的请求
        if path != '/ceshi':
            return

        count = 0
        # while websocket.open:
            # for i in range(10):
            #     count += 1
            #     # 创建一个字典并将其转换为JSON字符串
            #     message_dict = {"message": "你好", "count": count}
            #     message_json = json.dumps(message_dict)
            #     print(message_json)
            #     await websocket.send(message_json)  # 发送JSON字符串
            #     await asyncio.sleep(0.1)
            # await asyncio.sleep(1)

        # 创建一个字典并将其转换为JSON字符串
        message_dict = {"message": "你好", "count": count}
        message_json = json.dumps(message_dict)
        print(message_json)
        await websocket.send(message_json)  # 发送JSON字符串

    # 启动 WebScoket 服务器
    start_server = websockets.serve(echo, "0.0.0.0", 4399)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    webrun()
