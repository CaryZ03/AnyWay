# 前后端连接测试脚本
Write-Host "=== AnyWay 前后端连接测试 ===" -ForegroundColor Green

# 测试后端 API
Write-Host "`n1. 测试后端 API..." -ForegroundColor Yellow
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agents/" -UseBasicParsing -TimeoutSec 5
    $data = $backendResponse.Content | ConvertFrom-Json
    
    if ($data.code -eq 200) {
        Write-Host "✅ 后端 API 正常" -ForegroundColor Green
        Write-Host "   返回数据: $($data.data.Count) 个智能体" -ForegroundColor Cyan
    } else {
        Write-Host "❌ 后端 API 返回错误" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ 后端 API 无法访问" -ForegroundColor Red
    Write-Host "   错误: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试前端页面
Write-Host "`n2. 测试前端页面..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173/" -UseBasicParsing -TimeoutSec 5
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "✅ 前端页面正常" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ 前端页面无法访问" -ForegroundColor Red
    Write-Host "   错误: $($_.Exception.Message)" -ForegroundColor Red
}

# 测试数据库
Write-Host "`n3. 测试数据库连接..." -ForegroundColor Yellow
$mysqlStatus = docker ps --filter "name=aiagent-mysql" --format "{{.Status}}"
if ($mysqlStatus -like "*Up*") {
    Write-Host "✅ MySQL 数据库运行正常" -ForegroundColor Green
} else {
    Write-Host "❌ MySQL 数据库未运行" -ForegroundColor Red
}

# 测试 Redis
Write-Host "`n4. 测试 Redis 连接..." -ForegroundColor Yellow
$redisStatus = docker ps --filter "name=aiagent-redis" --format "{{.Status}}"
if ($redisStatus -like "*Up*") {
    Write-Host "✅ Redis 缓存运行正常" -ForegroundColor Green
} else {
    Write-Host "❌ Redis 缓存未运行" -ForegroundColor Red
}

Write-Host "`n=== 测试完成 ===" -ForegroundColor Green
Write-Host "`n访问地址:" -ForegroundColor Cyan
Write-Host "  前端: http://localhost:5173" -ForegroundColor White
Write-Host "  后端: http://localhost:8000/api/v1/" -ForegroundColor White
Write-Host "  文档: http://localhost:8000/swagger/" -ForegroundColor White
