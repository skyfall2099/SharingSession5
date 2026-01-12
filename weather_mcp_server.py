"""
Weather MCP Server Demo
一个简单的 MCP Server 示例，用于演示 MCP (Model Context Protocol) 的基本概念

使用方法：
1. 安装依赖: pip install mcp
2. 配置 Claude Desktop (详见 MCP_README.md)
3. 重启 Claude Desktop
4. 在对话中询问天气相关问题
"""

from mcp.server.fastmcp import FastMCP

# 创建 MCP Server 实例
# "weather" 是这个 server 的名称，会显示在 Claude Desktop 中
mcp = FastMCP("weather")

# 模拟的天气数据库
WEATHER_DATABASE = {
    "New York": {"temperature": 22, "condition": "Sunny", "humidity": 60},
    "London": {"temperature": 15, "condition": "Cloudy", "humidity": 75},
    "Tokyo": {"temperature": 28, "condition": "Rainy", "humidity": 80},
    "Paris": {"temperature": 18, "condition": "Partly Cloudy", "humidity": 65},
    "Beijing": {"temperature": 25, "condition": "Sunny", "humidity": 45},
    "Shanghai": {"temperature": 27, "condition": "Humid", "humidity": 85},
    "Sydney": {"temperature": 20, "condition": "Clear", "humidity": 55},
}


@mcp.tool()
def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    获取指定城市的当前天气信息

    Args:
        location: 城市名称，例如 "Tokyo", "New York", "London"
        unit: 温度单位，可选 "celsius"（摄氏度）或 "fahrenheit"（华氏度），默认为 celsius

    Returns:
        包含天气信息的字典：location, temperature, unit, condition, humidity
    """
    # 获取天气数据，如果城市不存在则返回默认值
    weather = WEATHER_DATABASE.get(
        location,
        {"temperature": 20, "condition": "Unknown", "humidity": 50}
    )

    temperature = weather["temperature"]

    # 根据单位转换温度
    if unit.lower() == "fahrenheit":
        temperature = round(temperature * 9/5 + 32, 1)
        unit_symbol = "F"
    else:
        unit_symbol = "C"

    return {
        "location": location,
        "temperature": temperature,
        "unit": unit_symbol,
        "condition": weather["condition"],
        "humidity": weather["humidity"]
    }


@mcp.tool()
def compare_weather(locations: list[str], unit: str = "celsius") -> dict:
    """
    比较多个城市的天气，找出最热、最冷、最潮湿的城市

    Args:
        locations: 城市名称列表，例如 ["Tokyo", "London", "Paris"]
        unit: 温度单位，可选 "celsius" 或 "fahrenheit"，默认为 celsius

    Returns:
        包含各城市天气信息和比较结果的字典
    """
    results = []

    for location in locations:
        weather = get_weather(location, unit)
        results.append(weather)

    if not results:
        return {"error": "No locations provided"}

    # 找出最热、最冷、最潮湿的城市
    warmest = max(results, key=lambda x: x["temperature"])
    coldest = min(results, key=lambda x: x["temperature"])
    most_humid = max(results, key=lambda x: x["humidity"])

    return {
        "weather_data": results,
        "comparison": {
            "warmest": {
                "location": warmest["location"],
                "temperature": warmest["temperature"],
                "unit": warmest["unit"]
            },
            "coldest": {
                "location": coldest["location"],
                "temperature": coldest["temperature"],
                "unit": coldest["unit"]
            },
            "most_humid": {
                "location": most_humid["location"],
                "humidity": most_humid["humidity"]
            }
        }
    }


@mcp.tool()
def list_available_cities() -> list[str]:
    """
    列出所有支持查询天气的城市

    Returns:
        支持的城市名称列表
    """
    return list(WEATHER_DATABASE.keys())


if __name__ == "__main__":
    # 启动 MCP Server
    # 使用 stdio 传输方式，这是 Claude Desktop 默认支持的方式
    mcp.run()
