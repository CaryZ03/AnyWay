"""
插件解析和调用服务
将 OpenAPI 规范转换为 Function Calling 格式，并支持调用插件
"""
import json
import logging
from typing import List, Dict, Any, Optional

import requests

from .models import Plugin

logger = logging.getLogger(__name__)


class PluginService:
    """插件服务"""

    @staticmethod
    def parse_openapi_to_functions(plugins: List[Plugin]) -> List[Dict[str, Any]]:
        """
        将插件的 OpenAPI 规范转换为 Function Calling 格式

        Args:
            plugins: 插件列表

        Returns:
            函数定义列表
        """
        functions = []

        for plugin in plugins:
            if not plugin.openapi_spec or plugin.status != "enabled":
                continue

            spec = plugin.openapi_spec
            paths = spec.get("paths", {})
            servers = spec.get("servers", [])
            base_url = servers[0]["url"] if servers else ""

            for path, methods in paths.items():
                for method, details in methods.items():
                    if method.lower() not in ["get", "post", "put", "delete", "patch"]:
                        continue

                    function = {
                        "name": details.get("operationId", f"{method}_{path.replace('/', '_')}"),
                        "description": details.get("summary") or details.get("description", ""),
                        "parameters": {"type": "object", "properties": {}, "required": []},
                        "metadata": {
                            "plugin_id": plugin.id,
                            "plugin_name": plugin.name,
                            "method": method.upper(),
                            "path": path,
                            "base_url": base_url,
                        },
                    }

                    # 解析路径参数和查询参数
                    if "parameters" in details:
                        for param in details["parameters"]:
                            if param["in"] in ["path", "query"]:
                                param_schema = param.get("schema", {})
                                function["parameters"]["properties"][param["name"]] = {
                                    "type": param_schema.get("type", "string"),
                                    "description": param.get("description", ""),
                                }
                                if param.get("required"):
                                    function["parameters"]["required"].append(param["name"])

                    # 解析请求体参数
                    if "requestBody" in details:
                        request_body = details["requestBody"]
                        content = request_body.get("content", {})
                        if "application/json" in content:
                            schema = content["application/json"].get("schema", {})
                            if "properties" in schema:
                                for prop_name, prop_schema in schema["properties"].items():
                                    function["parameters"]["properties"][prop_name] = {
                                        "type": prop_schema.get("type", "string"),
                                        "description": prop_schema.get("description", ""),
                                    }
                                    if prop_name in schema.get("required", []):
                                        function["parameters"]["required"].append(prop_name)

                    functions.append(function)

        return functions

    @staticmethod
    def call_function(
        function_name: str,
        arguments: Dict[str, Any],
        functions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        调用插件函数

        Args:
            function_name: 函数名称
            arguments: 函数参数
            functions: 函数定义列表

        Returns:
            函数调用结果
        """
        # 查找函数定义
        function_def = None
        for func in functions:
            if func["name"] == function_name:
                function_def = func
                break

        if not function_def:
            return {"error": f"函数 {function_name} 不存在"}

        metadata = function_def["metadata"]
        method = metadata["method"]
        path = metadata["path"]
        base_url = metadata["base_url"]

        # 构建完整 URL
        url = f"{base_url}{path}"

        # 替换路径参数
        for key, value in arguments.items():
            placeholder = f"{{{key}}}"
            if placeholder in url:
                url = url.replace(placeholder, str(value))

        # 分离路径参数和请求体参数
        path_params = {}
        query_params = {}
        body_params = {}

        for key, value in arguments.items():
            if f"{{{key}}}" in path:
                path_params[key] = value
            elif method in ["GET", "DELETE"]:
                query_params[key] = value
            else:
                body_params[key] = value

        try:
            # 发送请求
            if method == "GET":
                response = requests.get(url, params=query_params, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=body_params, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=body_params, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, params=query_params, timeout=30)
            elif method == "PATCH":
                response = requests.patch(url, json=body_params, timeout=30)
            else:
                return {"error": f"不支持的 HTTP 方法: {method}"}

            response.raise_for_status()

            # 返回结果
            try:
                return {
                    "success": True,
                    "data": response.json(),
                    "status_code": response.status_code,
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "data": response.text,
                    "status_code": response.status_code,
                }

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def format_function_result(result: Dict[str, Any]) -> str:
        """
        格式化函数调用结果为文本

        Args:
            result: 函数调用结果

        Returns:
            格式化后的文本
        """
        if not result.get("success"):
            return f"调用失败: {result.get('error', '未知错误')}"

        data = result.get("data")
        if isinstance(data, dict):
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif isinstance(data, str):
            return data
        else:
            return str(data)

    @staticmethod
    def build_api_map(plugin: Plugin) -> Dict[str, Dict[str, str]]:
        """
        将插件的 OpenAPI spec 转换为 {operation_id: {"url": ..., "method": ...}} 的字典

        Args:
            plugin: 插件对象

        Returns:
            API映射字典
        """
        api_map = {}
        if not plugin.openapi_spec:
            return api_map

        spec = plugin.openapi_spec
        servers = spec.get("servers", [])
        base_url = servers[0]["url"].rstrip("/") if servers else plugin.base_url.rstrip("/")

        paths = spec.get("paths", {})
        for path, methods in paths.items():
            for method, info in methods.items():
                op_id = info.get("operationId")
                if not op_id:
                    continue
                api_map[op_id] = {
                    "url": base_url + path,
                    "method": method.upper(),
                }
        return api_map

    @staticmethod
    def call_plugin_operation(
        plugin: Plugin, operation_id: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用插件的指定操作

        Args:
            plugin: 插件对象
            operation_id: 操作ID（operationId）
            params: 操作参数

        Returns:
            调用结果
        """
        if not plugin.openapi_spec:
            return {"error": "插件没有 OpenAPI 规范"}

        spec = plugin.openapi_spec
        servers = spec.get("servers", [])
        base_url = servers[0]["url"].rstrip("/") if servers else plugin.base_url.rstrip("/")

        paths = spec.get("paths", {})
        operation_info = None
        operation_path = None
        operation_method = None

        # 查找操作
        for path, methods in paths.items():
            for method, info in methods.items():
                if info.get("operationId") == operation_id:
                    operation_info = info
                    operation_path = path
                    operation_method = method.upper()
                    break
            if operation_info:
                break

        if not operation_info:
            return {"error": f"操作 {operation_id} 不存在"}

        # 构建完整 URL
        url = f"{base_url}{operation_path}"

        # 替换路径参数
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            if placeholder in url:
                url = url.replace(placeholder, str(value))

        # 分离参数
        query_params = {}
        body_params = {}
        path_placeholders = set()
        if operation_path:
            import re

            path_placeholders = set(re.findall(r"{(\w+)}", operation_path))

        for key, value in params.items():
            if key in path_placeholders:
                # 路径参数已经在URL替换中处理
                continue
            elif operation_method in ["GET", "DELETE"]:
                query_params[key] = value
            else:
                body_params[key] = value

        try:
            # 发送请求
            if operation_method == "GET":
                response = requests.get(url, params=query_params, timeout=30)
            elif operation_method == "POST":
                response = requests.post(url, json=body_params, timeout=30)
            elif operation_method == "PUT":
                response = requests.put(url, json=body_params, timeout=30)
            elif operation_method == "DELETE":
                response = requests.delete(url, params=query_params, timeout=30)
            elif operation_method == "PATCH":
                response = requests.patch(url, json=body_params, timeout=30)
            else:
                return {"error": f"不支持的 HTTP 方法: {operation_method}"}

            response.raise_for_status()

            # 返回结果
            try:
                result_data = response.json()
            except json.JSONDecodeError:
                result_data = response.text

            return {
                "success": True,
                "data": result_data,
                "status_code": response.status_code,
                "operation_id": operation_id,
                "plugin_id": plugin.id,
                "plugin_name": plugin.name,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"调用插件操作失败: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}


def create_plugin_service() -> PluginService:
    """创建插件服务实例"""
    return PluginService()


# ========== 向后兼容的函数 ==========
# 这些函数保留以保持与现有代码的兼容性


def build_tools_from_openapi(openapi_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    将 OpenAPI spec 转换为工具列表（向后兼容函数）

    Args:
        openapi_spec: OpenAPI 规范字典

    Returns:
        工具列表
    """
    tools = []
    for path, item in openapi_spec.get("paths", {}).items():
        for method, info in item.items():
            op_id = info.get("operationId")
            if not op_id:
                continue
            params_schema = {"type": "object", "properties": {}, "required": []}
            for p in info.get("parameters", []):
                name = p["name"]
                params_schema["properties"][name] = {
                    "type": p.get("schema", {}).get("type", "string")
                }
                if p.get("required", False):
                    params_schema["required"].append(name)
            if "requestBody" in info:
                body_schema = (
                    info["requestBody"]
                    .get("content", {})
                    .get("application/json", {})
                    .get("schema", {})
                )
                for name, prop in body_schema.get("properties", {}).items():
                    params_schema["properties"][name] = prop
                for req in body_schema.get("required", []):
                    params_schema["required"].append(req)
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": op_id,
                        "description": info.get("description", ""),
                        "parameters": params_schema,
                    },
                }
            )
    return tools


def build_api_map(openapi_spec: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    将 OpenAPI spec 转换为 {operation_id: {"url": ..., "method": ...}} 的字典（向后兼容函数）

    Args:
        openapi_spec: OpenAPI 规范字典

    Returns:
        API映射字典
    """
    api_map = {}
    base_url = openapi_spec["servers"][0]["url"].rstrip("/") if openapi_spec.get("servers") else ""
    for path, item in openapi_spec.get("paths", {}).items():
        for method, info in item.items():
            op_id = info.get("operationId")
            if not op_id:
                continue
            api_map[op_id] = {"url": base_url + path, "method": method.upper()}
    return api_map


def call_plugin(
    api_maps: Dict[int, Dict[str, Dict[str, str]]],
    plugin_id: int,
    operation_id: str,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    """
    调用插件操作（向后兼容函数）

    Args:
        api_maps: API映射字典，格式为 {plugin_id: {operation_id: {"url": ..., "method": ...}}}
        plugin_id: 插件ID
        operation_id: 操作ID
        params: 参数

    Returns:
        调用结果
    """
    api = api_maps.get(plugin_id, {}).get(operation_id)
    if not api:
        return {"error": f"operationId not found: {operation_id}"}

    url = api["url"]
    method = api["method"]

    try:
        if method == "GET":
            resp = requests.get(url, params=params, timeout=5)
        else:
            resp = requests.post(url, json=params, timeout=5)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}
