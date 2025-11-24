"""
自定义异常处理器
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    自定义异常处理器
    """
    # 调用REST framework默认的异常处理器
    response = exception_handler(exc, context)
    
    # 如果response为None，说明是未处理的异常
    if response is None:
        logger.error(f'Unhandled exception: {exc}', exc_info=True)
        return Response({
            'code': 500,
            'message': '服务器内部错误',
            'data': None,
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 自定义响应格式
    custom_response_data = {
        'code': response.status_code,
        'message': '请求失败',
        'data': None,
        'success': False
    }
    
    # 提取错误信息
    if isinstance(response.data, dict):
        if 'detail' in response.data:
            custom_response_data['message'] = response.data['detail']
        else:
            custom_response_data['data'] = response.data
    else:
        custom_response_data['message'] = str(response.data)
    
    response.data = custom_response_data
    
    return response
