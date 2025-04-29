import asyncio
import websockets
import json

connected_clients = set()

async def init_websocket(websocket, path):
    # 添加新的客户端连接
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # 处理接收到的消息
            data = json.loads(message)
            print(f"Received message: {data}")
    finally:
        # 移除断开的客户端连接
        connected_clients.remove(websocket)

async def broadcast_message():
    while True:
        if connected_clients:  # 只有在有客户端连接时才广播消息
            message = json.dumps({"type": "broadcast", "content": "This is a broadcast message"})
            await asyncio.gather(*(client.send(message) for client in connected_clients))
        await asyncio.sleep(5)  # 每5秒发送一次广播消息

async def broadcast_custom_message(message):
    if connected_clients:  # 只有在有客户端连接时才广播消息
        message = json.dumps({"type": "custom_broadcast", "content": message})
        await asyncio.gather(*(client.send(message) for client in connected_clients))

def start_server():
    server = websockets.serve(init_websocket, "0.0.0.0", 8765)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server)
    loop.create_task(broadcast_message())  # 启动定时广播任务
    return loop

if __name__ == "__main__":
    print("Starting WebSocket server...")
    loop = start_server()

    # 示例：通过函数广播自定义消息
    async def example_broadcast():
        await asyncio.sleep(10)  # 等待10秒后发送自定义广播消息
        await broadcast_custom_message("This is a custom broadcast message")

    loop.create_task(example_broadcast())  # 启动示例广播任务
    loop.run_forever()
