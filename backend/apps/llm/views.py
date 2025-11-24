"""
LLM服务视图
"""
from rest_framework.views import APIView
from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .services import get_llm_service
from utils.response import ApiResponse


class ChatRequestSerializer(serializers.Serializer):
    """聊天请求序列化器"""
    messages = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        help_text='消息列表'
    )
    model = serializers.CharField(
        default='gpt-3.5-turbo',
        help_text='模型名称'
    )
    temperature = serializers.FloatField(
        default=0.7,
        min_value=0,
        max_value=2,
        help_text='温度参数'
    )
    
    class Meta:
        ref_name = 'LLMChatRequest'


class ChatView(APIView):
    """
    LLM聊天接口
    """
    
    @swagger_auto_schema(
        operation_summary='LLM聊天',
        operation_description='调用LLM进行对话',
        request_body=ChatRequestSerializer,
        responses={200: openapi.Response('聊天成功', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reply': openapi.Schema(type=openapi.TYPE_STRING, description='模型回复')
            }
        ))}
    )
    def post(self, request):
        """聊天接口"""
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        messages = serializer.validated_data['messages']
        model = serializer.validated_data['model']
        temperature = serializer.validated_data['temperature']
        
        try:
            llm_service = get_llm_service('openai')
            reply = llm_service.chat(
                messages=messages,
                model=model,
                temperature=temperature
            )
            
            return ApiResponse.success(
                data={'reply': reply},
                message='聊天成功'
            )
        except Exception as e:
            return ApiResponse.error(message=f'聊天失败: {str(e)}')
