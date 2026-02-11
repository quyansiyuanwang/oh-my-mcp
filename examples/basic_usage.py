"""
MCP Server 基本使用示例

本示例演示如何创建和运行 MCP Server。
"""

from fastmcp import FastMCP
from mcp_server.tools import compression, web, file, data, text
from mcp_server.utils import logger


def main():
    """创建并运行 MCP Server"""

    # 创建 MCP 服务器实例
    mcp = FastMCP("Example MCP Server")

    logger.info("正在注册工具...")

    # 注册工具模块
    compression.register_tools(mcp)
    web.register_tools(mcp)
    file.register_tools(mcp)
    data.register_tools(mcp)
    text.register_tools(mcp)

    logger.info("工具注册完成！")

    # 添加自定义资源
    @mcp.resource("example://info")
    def get_info() -> str:
        """获取服务器信息"""
        import json
        return json.dumps({
            "name": "Example MCP Server",
            "version": "0.1.0",
            "tools": ["compression", "web", "file", "data", "text"]
        })

    logger.info("服务器准备就绪")

    # 运行服务器
    # 注意：这会阻塞，直到服务器停止
    mcp.run()


if __name__ == "__main__":
    main()
