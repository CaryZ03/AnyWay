#!/bin/bash
# 服务器状态检查脚本

SERVER="39.102.211.118"
PORT="18080"

echo "=== AnyWay 服务器状态检查 ==="

# 1. 检查端口连通性
echo "1. 检查端口连通性..."
if nc -z $SERVER $PORT; then
    echo "✓ 端口 $PORT 可访问"
else
    echo "✗ 端口 $PORT 不可访问"
fi

# 2. 检查 HTTP 响应
echo "2. 检查 HTTP 响应..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://$SERVER:$PORT/health/)
if [ "$HTTP_STATUS" = "200" ]; then
    echo "✓ 健康检查通过 (HTTP $HTTP_STATUS)"
else
    echo "✗ 健康检查失败 (HTTP $HTTP_STATUS)"
fi

# 3. 检查 API 可用性
echo "3. 检查 API 可用性..."
API_RESPONSE=$(curl -s http://$SERVER:$PORT/api/v1/agents/ | head -c 100)
if [[ $API_RESPONSE == *"code"* ]]; then
    echo "✓ API 响应正常"
else
    echo "✗ API 响应异常"
    echo "响应: $API_RESPONSE"
fi

# 4. 检查进程状态 (需要 SSH 访问)
echo "4. 检查服务进程..."
echo "请手动 SSH 到服务器检查:"
echo "ssh user@$SERVER 'ps aux | grep python'"
echo "ssh user@$SERVER 'sudo systemctl status anyway'"

echo "=== 检查完成 ==="
