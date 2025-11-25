"""
统一响应格式工具类
"""
from rest_framework.response import Response
from rest_framework import status


class ApiResponse:
    """统一API响应格式"""
    
    @staticmethod
    def success(data=None, message='操作成功', code=200):
        """成功响应"""
        return Response({
            'code': code,
            'message': message,
            'data': data,
            'success': True
        }, status=status.HTTP_200_OK)
    
    @staticmethod
    def error(message='操作失败', code=400, data=None):
        """错误响应"""
        return Response({
            'code': code,
            'message': message,
            'data': data,
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def created(data=None, message='创建成功'):
        """创建成功响应"""
        return Response({
            'code': 201,
            'message': message,
            'data': data,
            'success': True
        }, status=status.HTTP_201_CREATED)
    
    @staticmethod
    def not_found(message='资源不存在'):
        """资源不存在响应"""
        return Response({
            'code': 404,
            'message': message,
            'data': None,
            'success': False
        }, status=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def server_error(message='服务器错误'):
        """服务器错误响应"""
        return Response({
            'code': 500,
            'message': message,
            'data': None,
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
