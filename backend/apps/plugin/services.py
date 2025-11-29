import requests


def build_tools_from_openapi(openai_spec):
    tools = []
    for path, item in openai_spec.get("paths", {}).items():
        for method, info in item.items():
            op_id = info.get("operationId")
            if not op_id:
                continue
            params_schema = {"type": "object", "properties": {}, "required": []}
            for p in info.get("parameters", []):
                name = p["name"]
                params_schema["properties"][name] = {"type": p.get("schema", {}).get("type", "string")}
                if p.get("required", False):
                    params_schema["required"].append(name)
            if "requestBody" in info:
                body_schema = info["requestBody"].get("content", {}).get("application/json", {}).get("schema", {})
                for name, prop in body_schema.get("properties", {}).items():
                    params_schema["properties"][name] = prop
                for req in body_schema.get("required", []):
                    params_schema["required"].append(req)
            tools.append({
                "type": "function",
                "function": {
                    "name": op_id,
                    "description": info.get("description", ""),
                    "parameters": params_schema
                }
            })
    return tools


def build_api_map(openai_spec):
    """
    将 OpenAPI spec 转换为 {operation_id: {"url": ..., "method": ...}} 的字典
    """
    api_map = {}
    base_url = openai_spec["servers"][0]["url"].rstrip("/")
    for path, item in openai_spec.get("paths", {}).items():
        for method, info in item.items():
            op_id = info.get("operationId")
            if not op_id:
                continue
            api_map[op_id] = {
                "url": base_url + path,
                "method": method.upper()
            }
    return api_map


def call_plugin(api_maps, plugin_id, operation_id, params):
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

