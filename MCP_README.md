# MCP (Model Context Protocol) 示例

## 什么是 MCP？

MCP (Model Context Protocol) 是 Anthropic 推出的开放协议，用于标准化 AI 助手与外部工具/数据源之间的通信。

### MCP vs Function Calling

| 特性 | Function Calling | MCP |
|------|-----------------|-----|
| 工具定义位置 | 应用代码内部 | 独立的 MCP Server |
| 复用性 | 单一应用 | 多客户端共享 |
| 架构模式 | 单体 | Client-Server |
| 工具发现 | 手动配置 | 协议自动发现 |

**简单理解**：Function Calling 是"内置工具"，MCP 是"外挂工具服务"。

## 架构图

```
┌─────────────────┐      stdio       ┌─────────────────────┐
│  Claude Desktop │ <===============>│  weather_mcp_server │
│  (MCP Client)   │    JSON-RPC      │  (MCP Server)       │
└─────────────────┘                  └─────────────────────┘
        │                                      │
        │  1. 启动时连接                         │
        │  2. 询问可用工具 ──────────────────────>│
        │  3. 返回工具列表 <──────────────────────│
        │  4. 用户对话时调用工具 ─────────────────>│
        │  5. 返回工具执行结果 <──────────────────│
        │                                      │
```

## 快速开始

### 1. 安装依赖

```bash
pip install mcp
```

### 2. 测试 MCP Server（可选）

在命令行中测试 server 是否能正常启动：

```bash
python weather_mcp_server.py
```

如果没有报错，说明 server 可以正常运行。按 `Ctrl+C` 退出。

### 3. 配置 Claude Desktop

找到 Claude Desktop 的配置文件：

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

编辑配置文件，添加以下内容：

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["D:/git/SharingSession5/weather_mcp_server.py"]
    }
  }
}
```

> **注意**：请将路径替换为你实际的文件路径。

如果已有其他配置，只需在 `mcpServers` 对象中添加 `weather` 配置即可。

### 4. 重启 Claude Desktop

关闭并重新打开 Claude Desktop，它会自动启动并连接到你的 MCP Server。

### 5. 测试

在 Claude Desktop 中尝试以下对话：

- "东京天气怎么样？"
- "帮我查一下纽约的天气，用华氏度显示"
- "比较一下东京、伦敦和巴黎的天气，哪个最热？"
- "有哪些城市可以查询天气？"

## 提供的工具

本示例 MCP Server 提供了 3 个工具：

### 1. `get_weather`

获取单个城市的天气信息。

**参数**：
- `location` (string, 必填): 城市名称
- `unit` (string, 可选): 温度单位，"celsius" 或 "fahrenheit"

**示例返回**：
```json
{
  "location": "Tokyo",
  "temperature": 28,
  "unit": "C",
  "condition": "Rainy",
  "humidity": 80
}
```

### 2. `compare_weather`

比较多个城市的天气。

**参数**：
- `locations` (list[string], 必填): 城市名称列表
- `unit` (string, 可选): 温度单位

**示例返回**：
```json
{
  "weather_data": [...],
  "comparison": {
    "warmest": {"location": "Tokyo", "temperature": 28, "unit": "C"},
    "coldest": {"location": "London", "temperature": 15, "unit": "C"},
    "most_humid": {"location": "Shanghai", "humidity": 85}
  }
}
```

### 3. `list_available_cities`

列出所有支持的城市。

**返回**：
```json
["New York", "London", "Tokyo", "Paris", "Beijing", "Shanghai", "Sydney"]
```

## 支持的城市

| 城市 | 温度 (°C) | 天气状况 | 湿度 (%) |
|------|----------|---------|---------|
| New York | 22 | Sunny | 60 |
| London | 15 | Cloudy | 75 |
| Tokyo | 28 | Rainy | 80 |
| Paris | 18 | Partly Cloudy | 65 |
| Beijing | 25 | Sunny | 45 |
| Shanghai | 27 | Humid | 85 |
| Sydney | 20 | Clear | 55 |

## 代码结构说明

```python
from mcp.server.fastmcp import FastMCP

# 创建 MCP Server
mcp = FastMCP("weather")

# 使用装饰器注册工具
@mcp.tool()
def get_weather(location: str, unit: str = "celsius") -> dict:
    """工具描述（Claude 会看到这个描述来决定何时调用）"""
    # 工具实现
    return {...}

# 启动 server
mcp.run()
```

关键点：
1. `FastMCP` - MCP SDK 提供的简化 API
2. `@mcp.tool()` - 装饰器，将函数注册为 MCP 工具
3. 函数的 docstring 会作为工具描述，帮助 Claude 理解何时使用该工具
4. 类型注解（如 `str`, `dict`）会被转换为 JSON Schema，用于参数验证

## 常见问题

### Q: Claude Desktop 没有调用我的工具？

1. 检查配置文件路径是否正确
2. 确保 Python 在系统 PATH 中
3. 查看 Claude Desktop 的日志（Help → Show Logs）
4. 尝试重启 Claude Desktop

### Q: 如何调试 MCP Server？

可以添加日志输出到文件：

```python
import logging
logging.basicConfig(filename='mcp_server.log', level=logging.DEBUG)
```

### Q: 如何添加新工具？

只需添加新的函数并使用 `@mcp.tool()` 装饰器：

```python
@mcp.tool()
def new_tool(param1: str, param2: int) -> dict:
    """工具描述"""
    return {"result": "..."}
```

## 参考资料

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [MCP GitHub](https://github.com/modelcontextprotocol)
- [Anthropic MCP 公告](https://www.anthropic.com/news/model-context-protocol)
