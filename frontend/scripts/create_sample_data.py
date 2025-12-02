#!/usr/bin/env python
"""
创建样例数据脚本
用于生成测试用的智能体、插件和知识库
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiagent.settings')
django.setup()

from apps.agent.models import Agent
from apps.plugin.models import Plugin
from apps.knowledge.models import KnowledgeBase
from django.contrib.auth import get_user_model
import json

User = get_user_model()

def create_sample_agents():
    """创建样例智能体"""
    print("创建样例智能体...")
    
    agents_data = [
        {
            'name': '编程助手',
            'description': '一个专业的编程学习助手，可以帮助你学习各种编程语言，解释代码，提供编程练习和解答编程问题。',
            'system_prompt': '你是一个专业的编程导师，擅长多种编程语言（Python、JavaScript、Java、C++等）。你的任务是帮助用户学习编程，解释代码概念，提供编程练习，并解答编程问题。请用清晰、易懂的方式回答问题。',
            'user_prompt_template': '{user_input}',
            'model_config': json.dumps({
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'max_tokens': 2000
            }),
            'status': 'published'
        },
        {
            'name': '英语学习助手',
            'description': '帮助你学习英语，提供单词解释、语法讲解、口语练习等功能。',
            'system_prompt': '你是一个专业的英语教师，擅长帮助用户学习英语。你可以解释单词、讲解语法、提供口语练习建议，并纠正用户的英语错误。请用耐心、鼓励的方式教学。',
            'user_prompt_template': '{user_input}',
            'model_config': json.dumps({
                'model': 'gpt-3.5-turbo',
                'temperature': 0.8,
                'max_tokens': 1500
            }),
            'status': 'published'
        },
        {
            'name': '创意写作助手',
            'description': '帮助你进行创意写作，提供故事构思、情节发展、角色塑造等建议。',
            'system_prompt': '你是一个富有创造力的写作导师，擅长帮助用户进行创意写作。你可以提供故事构思、情节发展建议、角色塑造技巧，并帮助用户改进他们的作品。请用启发性的方式引导用户。',
            'user_prompt_template': '{user_input}',
            'model_config': json.dumps({
                'model': 'gpt-4',
                'temperature': 0.9,
                'max_tokens': 2500
            }),
            'status': 'draft'
        },
        {
            'name': '数据分析助手',
            'description': '帮助你分析数据，提供数据可视化建议和统计分析方法。',
            'system_prompt': '你是一个数据分析专家，擅长数据分析和统计。你可以帮助用户理解数据、选择合适的数据分析方法、解释统计结果，并提供数据可视化建议。',
            'user_prompt_template': '{user_input}',
            'model_config': json.dumps({
                'model': 'gpt-4',
                'temperature': 0.5,
                'max_tokens': 2000
            }),
            'status': 'published'
        }
    ]
    
    created_count = 0
    for agent_data in agents_data:
        agent, created = Agent.objects.get_or_create(
            name=agent_data['name'],
            defaults=agent_data
        )
        if created:
            created_count += 1
            print(f"  ✓ 创建智能体: {agent.name}")
        else:
            print(f"  - 智能体已存在: {agent.name}")
    
    print(f"完成！创建了 {created_count} 个智能体\n")
    return created_count


def create_sample_plugins():
    """创建样例插件"""
    print("创建样例插件...")
    
    plugins_data = [
        {
            'name': '天气查询插件',
            'description': '查询指定城市的天气信息，包括温度、湿度、风速等。',
            'openapi_spec': json.dumps({
                'openapi': '3.0.0',
                'info': {
                    'title': 'Weather API',
                    'version': '1.0.0'
                },
                'paths': {
                    '/weather': {
                        'get': {
                            'summary': 'Get weather',
                            'parameters': [
                                {
                                    'name': 'city',
                                    'in': 'query',
                                    'required': True,
                                    'schema': {'type': 'string'}
                                }
                            ]
                        }
                    }
                }
            }),
            'base_url': 'https://api.weather.example.com',
            'auth_config': json.dumps({
                'type': 'api_key',
                'api_key': 'your-api-key'
            }),
            'status': 'enabled'
        },
        {
            'name': '翻译插件',
            'description': '支持多语言翻译，可以将文本翻译成多种语言。',
            'openapi_spec': json.dumps({
                'openapi': '3.0.0',
                'info': {
                    'title': 'Translation API',
                    'version': '1.0.0'
                },
                'paths': {
                    '/translate': {
                        'post': {
                            'summary': 'Translate text',
                            'requestBody': {
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'text': {'type': 'string'},
                                                'target_lang': {'type': 'string'}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }),
            'base_url': 'https://api.translate.example.com',
            'auth_config': json.dumps({
                'type': 'bearer',
                'token': 'your-token'
            }),
            'status': 'enabled'
        },
        {
            'name': '计算器插件',
            'description': '执行数学计算，支持基本运算和科学计算。',
            'openapi_spec': json.dumps({
                'openapi': '3.0.0',
                'info': {
                    'title': 'Calculator API',
                    'version': '1.0.0'
                },
                'paths': {
                    '/calculate': {
                        'post': {
                            'summary': 'Calculate expression',
                            'requestBody': {
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'expression': {'type': 'string'}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }),
            'base_url': 'https://api.calc.example.com',
            'auth_config': json.dumps({}),
            'status': 'enabled'
        }
    ]
    
    created_count = 0
    for plugin_data in plugins_data:
        plugin, created = Plugin.objects.get_or_create(
            name=plugin_data['name'],
            defaults=plugin_data
        )
        if created:
            created_count += 1
            print(f"  ✓ 创建插件: {plugin.name}")
        else:
            print(f"  - 插件已存在: {plugin.name}")
    
    print(f"完成！创建了 {created_count} 个插件\n")
    return created_count


def create_sample_knowledge_bases():
    """创建样例知识库"""
    print("创建样例知识库...")
    
    knowledge_bases_data = [
        {
            'name': 'Python 编程知识库',
            'description': '包含 Python 编程语言的基础知识、常用库和最佳实践。',
            'embedding_model': 'text-embedding-ada-002'
        },
        {
            'name': '机器学习知识库',
            'description': '包含机器学习算法、深度学习框架和模型训练相关的知识。',
            'embedding_model': 'text-embedding-ada-002'
        },
        {
            'name': '产品文档知识库',
            'description': '包含产品使用文档、API 文档和常见问题解答。',
            'embedding_model': 'text-embedding-ada-002'
        }
    ]
    
    created_count = 0
    for kb_data in knowledge_bases_data:
        kb, created = KnowledgeBase.objects.get_or_create(
            name=kb_data['name'],
            defaults=kb_data
        )
        if created:
            created_count += 1
            print(f"  ✓ 创建知识库: {kb.name}")
        else:
            print(f"  - 知识库已存在: {kb.name}")
    
    print(f"完成！创建了 {created_count} 个知识库\n")
    return created_count


def main():
    """主函数"""
    print("=" * 50)
    print("开始创建样例数据...")
    print("=" * 50 + "\n")
    
    agents_count = create_sample_agents()
    plugins_count = create_sample_plugins()
    knowledge_bases_count = create_sample_knowledge_bases()
    
    print("=" * 50)
    print("样例数据创建完成！")
    print("=" * 50)
    print(f"总计:")
    print(f"  - 智能体: {agents_count} 个")
    print(f"  - 插件: {plugins_count} 个")
    print(f"  - 知识库: {knowledge_bases_count} 个")
    print("=" * 50)


if __name__ == '__main__':
    main()

