const WebSocket = require('ws');

const ws = new WebSocket('ws://103.242.3.44:3000'); // 替换为云服务器的 IP 地址和端口

ws.on('open', function open() {
    console.log('Connected to WebSocket proxy server');
    ws.send('Hello, server!');
});

ws.on('message', function incoming(data) {
    console.log(`Received: ${data}`);
});
