# API接口测试脚本
# 使用方法: .\test_api.ps1

$baseUrl = "http://localhost:8000"
$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AnyWay API 接口测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 测试1: 健康检查
Write-Host "[1] 测试健康检查接口" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health/" -Method Get
    Write-Host "✓ 健康检查成功" -ForegroundColor Green
    $response | ConvertTo-Json
} catch {
    Write-Host "✗ 健康检查失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试2: 获取智能体列表
Write-Host "[2] 测试获取智能体列表" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/agents/" -Method Get -Headers $headers
    Write-Host "✓ 获取智能体列表成功" -ForegroundColor Green
    Write-Host "智能体数量: $($response.data.Count)" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ 获取智能体列表失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试3: 创建智能体
Write-Host "[3] 测试创建智能体" -ForegroundColor Yellow
$agentData = @{
    name = "测试智能体"
    description = "这是一个API测试创建的智能体"
    system_prompt = "你是一个友好的AI助手"
    model_config = @{
        model = "gpt-3.5-turbo"
        temperature = 0.7
    }
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/agents/" -Method Post -Headers $headers -Body $agentData
    Write-Host "✓ 创建智能体成功" -ForegroundColor Green
    $agentId = $response.data.id
    Write-Host "智能体ID: $agentId" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ 创建智能体失败: $($_.Exception.Message)" -ForegroundColor Red
    $agentId = $null
}
Write-Host ""

# 测试4: 获取智能体详情
if ($agentId) {
    Write-Host "[4] 测试获取智能体详情 (ID: $agentId)" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/agents/$agentId/" -Method Get -Headers $headers
        Write-Host "✓ 获取智能体详情成功" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3
    } catch {
        Write-Host "✗ 获取智能体详情失败: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# 测试5: 更新智能体
if ($agentId) {
    Write-Host "[5] 测试更新智能体 (ID: $agentId)" -ForegroundColor Yellow
    $updateData = @{
        description = "更新后的描述"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/agents/$agentId/" -Method Patch -Headers $headers -Body $updateData
        Write-Host "✓ 更新智能体成功" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3
    } catch {
        Write-Host "✗ 更新智能体失败: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# 测试6: 发布智能体
if ($agentId) {
    Write-Host "[6] 测试发布智能体 (ID: $agentId)" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/agents/$agentId/publish/" -Method Post -Headers $headers
        Write-Host "✓ 发布智能体成功" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3
    } catch {
        Write-Host "✗ 发布智能体失败: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# 测试7: 测试智能体对话
if ($agentId) {
    Write-Host "[7] 测试智能体对话 (ID: $agentId)" -ForegroundColor Yellow
    $chatData = @{
        message = "你好，请介绍一下自己"
        context = @{}
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/agents/$agentId/test/" -Method Post -Headers $headers -Body $chatData
        Write-Host "✓ 智能体对话测试成功" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3
    } catch {
        Write-Host "✗ 智能体对话测试失败: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# 测试8: 获取工作流列表
Write-Host "[8] 测试获取工作流列表" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/workflows/" -Method Get -Headers $headers
    Write-Host "✓ 获取工作流列表成功" -ForegroundColor Green
    Write-Host "工作流数量: $($response.data.Count)" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ 获取工作流列表失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试9: 创建工作流
Write-Host "[9] 测试创建工作流" -ForegroundColor Yellow
$workflowData = @{
    name = "测试工作流"
    description = "API测试工作流"
    definition = @{
        nodes = @(
            @{
                id = "node1"
                type = "start"
                name = "开始"
            }
        )
        edges = @()
    }
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/workflows/" -Method Post -Headers $headers -Body $workflowData
    Write-Host "✓ 创建工作流成功" -ForegroundColor Green
    $workflowId = $response.data.id
    Write-Host "工作流ID: $workflowId" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ 创建工作流失败: $($_.Exception.Message)" -ForegroundColor Red
    $workflowId = $null
}
Write-Host ""

# 测试10: 获取知识库列表
Write-Host "[10] 测试获取知识库列表" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/knowledge/" -Method Get -Headers $headers
    Write-Host "✓ 获取知识库列表成功" -ForegroundColor Green
    Write-Host "知识库数量: $($response.data.Count)" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ 获取知识库列表失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试11: 创建知识库
Write-Host "[11] 测试创建知识库" -ForegroundColor Yellow
$knowledgeData = @{
    name = "测试知识库"
    description = "API测试知识库"
    embedding_model = "text-embedding-ada-002"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/knowledge/" -Method Post -Headers $headers -Body $knowledgeData
    Write-Host "✓ 创建知识库成功" -ForegroundColor Green
    $knowledgeId = $response.data.id
    Write-Host "知识库ID: $knowledgeId" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ 创建知识库失败: $($_.Exception.Message)" -ForegroundColor Red
    $knowledgeId = $null
}
Write-Host ""

# 测试12: 获取插件列表
Write-Host "[12] 测试获取插件列表" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/plugins/" -Method Get -Headers $headers
    Write-Host "✓ 获取插件列表成功" -ForegroundColor Green
    Write-Host "插件数量: $($response.data.Count)" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ 获取插件列表失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 测试13: 创建插件
Write-Host "[13] 测试创建插件" -ForegroundColor Yellow
$pluginData = @{
    name = "测试插件"
    description = "API测试插件"
    base_url = "https://api.example.com"
    openapi_spec = @{
        openapi = "3.0.0"
        info = @{
            title = "Test Plugin"
            version = "1.0.0"
        }
        paths = @{
            "/test" = @{
                get = @{
                    summary = "Test endpoint"
                    responses = @{
                        "200" = @{
                            description = "Success"
                        }
                    }
                }
            }
        }
    }
    auth_config = @{}
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/plugins/" -Method Post -Headers $headers -Body $pluginData
    Write-Host "✓ 创建插件成功" -ForegroundColor Green
    $pluginId = $response.data.id
    Write-Host "插件ID: $pluginId" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ 创建插件失败: $($_.Exception.Message)" -ForegroundColor Red
    $pluginId = $null
}
Write-Host ""

# 测试14: LLM聊天接口
Write-Host "[14] 测试LLM聊天接口" -ForegroundColor Yellow
$llmChatData = @{
    messages = @(
        @{
            role = "user"
            content = "Hello, how are you?"
        }
    )
    model = "gpt-3.5-turbo"
    temperature = 0.7
} | ConvertTo-Json -Depth 3

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/llm/chat/" -Method Post -Headers $headers -Body $llmChatData
    Write-Host "✓ LLM聊天接口测试成功" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "✗ LLM聊天接口测试失败: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 清理测试数据
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "清理测试数据" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 删除测试智能体
if ($agentId) {
    Write-Host "删除测试智能体 (ID: $agentId)" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/agents/$agentId/" -Method Delete -Headers $headers
        Write-Host "✓ 删除成功" -ForegroundColor Green
    } catch {
        Write-Host "✗ 删除失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 删除测试工作流
if ($workflowId) {
    Write-Host "删除测试工作流 (ID: $workflowId)" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/workflows/$workflowId/" -Method Delete -Headers $headers
        Write-Host "✓ 删除成功" -ForegroundColor Green
    } catch {
        Write-Host "✗ 删除失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 删除测试知识库
if ($knowledgeId) {
    Write-Host "删除测试知识库 (ID: $knowledgeId)" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/knowledge/$knowledgeId/" -Method Delete -Headers $headers
        Write-Host "✓ 删除成功" -ForegroundColor Green
    } catch {
        Write-Host "✗ 删除失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 删除测试插件
if ($pluginId) {
    Write-Host "删除测试插件 (ID: $pluginId)" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/v1/plugins/$pluginId/" -Method Delete -Headers $headers
        Write-Host "✓ 删除成功" -ForegroundColor Green
    } catch {
        Write-Host "✗ 删除失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "测试完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
