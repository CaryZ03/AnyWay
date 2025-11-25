#!/bin/bash
# 服务器诊断脚本

echo "=== AnyWay 服务器诊断 ==="

SERVER="39.102.211.118"
PORT="18080"

echo "1. 检查网络连通性..."
if ping -c 3 $SERVER > /dev/null 2>&1; then
    echo "✓ 服务器 $SERVER 可以 ping 通"
else
    echo "✗ 服务器 $SERVER 无法 ping 通"
fi

echo "2. 检查端口可达性..."
if timeout 5 bash -c "</dev/tcp/$SERVER/$PORT" 2>/dev/null; then
    echo "✓ 端口 $PORT 可以连接"
else
    echo "✗ 端口 $PORT 无法连接"
fi

echo "3. 检查 HTTP 响应..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://$SERVER:$PORT/health/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ HTTP 响应正常 (200)"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "✗ 无法建立 HTTP 连接"
else
    echo "✗ HTTP 响应异常 ($HTTP_CODE)"
fi

echo "4. 路由跟踪..."
traceroute $SERVER 2>/dev/null | head -5

echo "=== 诊断完成 ==="
echo ""
echo "如果端口无法连接，请检查："
echo "- 服务器防火墙: sudo ufw status"
echo "- 云服务商安全组设置"
echo "- Django 服务绑定地址: 应该是 0.0.0.0 而不是 127.0.0.1"
echo "- 服务是否正在运行: ps aux | grep python"
