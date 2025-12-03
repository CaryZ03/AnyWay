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
    
    # 记录原始异常和响应数据
    logger.warning(f'Exception handler called: {type(exc).__name__}, response: {response}')
    if response:
        logger.warning(f'Response data: {response.data}')
    
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
        logger.warning(f'Processing error data: {response.data}')
        
        # 处理 detail 字段（通常是通用错误）
        if 'detail' in response.data:
            custom_response_data['message'] = response.data['detail']
            logger.warning(f'Using detail message: {response.data["detail"]}')
        # 处理验证错误（字段级错误）
        elif 'non_field_errors' in response.data:
            # 非字段错误
            errors = response.data['non_field_errors']
            if isinstance(errors, list) and len(errors) > 0:
                custom_response_data['message'] = errors[0]
            else:
                custom_response_data['message'] = str(errors)
            custom_response_data['data'] = response.data
            logger.warning(f'Using non_field_errors: {custom_response_data["message"]}')
        else:
            # 字段级验证错误，提取第一个错误信息
            error_messages = []
            for field, errors in response.data.items():
                if isinstance(errors, list):
                    for error in errors:
                        if isinstance(error, dict) and 'message' in error:
                            error_messages.append(f'{field}: {error["message"]}')
                        else:
                            error_messages.append(f'{field}: {error}')
                elif isinstance(errors, dict):
                    # 处理嵌套的错误对象
                    if 'message' in errors:
                        error_messages.append(f'{field}: {errors["message"]}')
                    else:
                        error_messages.append(f'{field}: {str(errors)}')
                else:
                    error_messages.append(f'{field}: {errors}')
            
            if error_messages:
                custom_response_data['message'] = error_messages[0]
                # 保留完整的错误信息在 data 中
                custom_response_data['data'] = response.data
                logger.warning(f'Using field errors: {custom_response_data["message"]}, all errors: {error_messages}')
            else:
                custom_response_data['data'] = response.data
                logger.warning(f'No error messages extracted, keeping original data: {response.data}')
    else:
        custom_response_data['message'] = str(response.data)
        logger.warning(f'Response data is not dict, using string: {response.data}')
    
    # 记录最终的错误信息
    logger.warning(f'Final error response: message={custom_response_data["message"]}, data={custom_response_data.get("data")}')
    
    response.data = custom_response_data
    
    return response
