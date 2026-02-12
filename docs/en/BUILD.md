# MCP Server Build Guide

本文档说明如何在 Windows 和 Linux 上打包 MCP Server。

## 📋 前提条件

- Python 3.12 或更高版本
- 已安装项目依赖：`pip install -e .`
- PyInstaller 将自动安装（如果缺失）

## 🚀 快速开始

### Windows

```powershell
# 方式 1: 使用批处理脚本
cd scripts\build
.\build.bat

# 方式 2: 直接使用 Python
python ..\..\scripts\build\build.py
```

### Linux / macOS

```bash
# 方式 1: 使用 shell 脚本
cd scripts/build
chmod +x build.sh
./build.sh

# 方式 2: 直接使用 Python
python3 ../../scripts/build/build.py
```

## 📦 打包选项

### 1. 目录模式（推荐，启动更快）

生成一个包含所有依赖的目录：

```bash
python scripts/build/build.py
```

**输出位置**：

- Windows: `dist/mcp-server/mcp-server.exe`
- Linux: `dist/mcp-server/mcp-server`

**优点**：

- ✅ 启动速度快
- ✅ 便于调试
- ✅ 文件大小适中

**缺点**：

- ❌ 需要分发整个目录

### 2. 单文件模式（便于分发）

生成一个独立的可执行文件：

```bash
python scripts/build/build.py --onefile
# 或简写
python scripts/build/build.py -F
```

**输出位置**：

- Windows: `dist/mcp-server.exe`
- Linux: `dist/mcp-server`

**优点**：

- ✅ 只有一个文件
- ✅ 便于分发和部署

**缺点**：

- ❌ 首次启动较慢（需解压到临时目录）
- ❌ 文件稍大

### 3. 清理构建

清理之前的构建产物后重新构建：

```bash
python scripts/build/build.py --clean
# 或结合其他选项
python scripts/build/build.py --clean --onefile
```

## 🔧 命令行参数

| 参数        | 简写 | 描述                   |
| ----------- | ---- | ---------------------- |
| `--onefile` | `-F` | 构建为单个可执行文件   |
| `--clean`   | `-c` | 构建前清理旧的构建产物 |
| `--help`    | `-h` | 显示帮助信息           |

## 📝 使用示例

```bash
# 基本构建（目录模式）
python scripts/build/build.py

# 单文件构建
python scripts/build/build.py --onefile

# 清理后构建目录模式
python scripts/build/build.py --clean

# 清理后构建单文件
python scripts/build/build.py --clean --onefile

# 在 Windows 上使用批处理
scripts\build\build.bat --onefile

# 在 Linux 上使用 shell 脚本
scripts/build/build.sh --clean --onefile
```

## 🎯 配置 Claude Desktop

构建完成后，需要在 Claude Desktop 中配置 MCP 服务器。

### Windows

编辑配置文件：

```
%APPDATA%\Claude\claude_desktop_config.json
```

添加配置：

```json
{
  "mcpServers": {
    "comprehensive-mcp": {
      "command": "D:\\Developments\\mcp-server\\dist\\mcp-server\\mcp-server.exe"
    }
  }
}
```

### Linux / macOS

编辑配置文件：

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

添加配置：

```json
{
  "mcpServers": {
    "comprehensive-mcp": {
      "command": "/path/to/mcp-server/dist/mcp-server/mcp-server"
    }
  }
}
```

**注意**：使用绝对路径，并根据您选择的打包模式（目录 vs 单文件）调整路径。

## 🧪 测试构建

构建完成后，可以直接运行测试：

### Windows

```powershell
.\dist\mcp-server\mcp-server.exe
# 或单文件版本
.\dist\mcp-server.exe
```

### Linux / macOS

```bash
./dist/mcp-server/mcp-server
# 或单文件版本
./dist/mcp-server
```

服务器应该启动并显示：

```
============================================================
Starting Comprehensive MCP Server v0.1.0
============================================================
...
Server ready to accept connections.
============================================================
```

使用 `Ctrl+C` 停止服务器。

## 📦 分发

### 目录模式分发

打包整个 `dist/mcp-server/` 目录：

```bash
# Windows
cd dist
Compress-Archive -Path mcp-server -DestinationPath mcp-server-windows.zip

# Linux
cd dist
tar -czf mcp-server-linux.tar.gz mcp-server/
```

### 单文件分发

直接分发 `dist/mcp-server.exe` (Windows) 或 `dist/mcp-server` (Linux)。

## 🔍 故障排除

### 问题：找不到 PyInstaller

**解决方案**：

```bash
pip install pyinstaller
```

### 问题：导入错误或模块缺失

**解决方案**：

1. 确保已安装所有依赖：`pip install -e .`
2. 重新构建：`python scripts/build/build.py --clean`

### 问题：构建成功但运行时出错

**解决方案**：

1. 检查 `mcp_server.log` 日志文件
2. 尝试使用目录模式而非单文件模式
3. 检查是否缺少数据文件

### 问题：文件太大

**解决方案**：

1. 使用目录模式（比单文件小）
2. 检查是否有不必要的依赖被包含
3. 考虑使用 UPX 压缩（需额外配置）

## 🛠️ 高级配置

如果需要自定义构建过程，可以编辑 `scripts/build/build.py`：

- **添加隐藏导入**：修改 `get_hidden_imports()` 函数
- **添加数据文件**：修改 `get_data_files()` 函数
- **排除模块**：修改 `build_executable()` 中的 `excludes` 列表

## 📚 相关文档

- [PyInstaller 文档](https://pyinstaller.org/en/stable/)
- [MCP 协议](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://gofastmcp.com/)

## 💡 提示

1. **首选目录模式**：除非必须单文件分发，否则推荐目录模式（启动更快）
2. **定期清理**：使用 `--clean` 选项避免旧文件干扰
3. **测试构建**：每次构建后都应该测试运行
4. **使用虚拟环境**：确保在虚拟环境中构建，避免包含不必要的系统包

## 🎉 完成

现在您已经知道如何在 Windows 和 Linux 上打包 MCP Server 了！

如有问题，请查看 `mcp_server.log` 日志文件或提交 issue。

## 🤖 CI/CD 自动构建

### GitHub Actions 自动发布

本项目配置了自动化构建和发布流程，支持多平台构建：

**触发方式：**

1. **推送 tag**：推送以 `v` 开头的 tag（如 `v1.0.0`）

   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **手动触发**：在 GitHub Actions 页面手动运行 workflow
   - 进入仓库的 **Actions** 标签
   - 选择 **Build and Release** workflow
   - 点击 **Run workflow**
   - 输入版本号（如 `v1.0.1`）

**构建平台：**

- ✅ Windows (x64)
- ✅ Linux (x64)
- ✅ macOS (Intel x64)
- ✅ macOS (Apple Silicon arm64)

**输出产物：**

每个平台会生成打包好的压缩包，包含：

- 可执行文件
- USAGE.md 使用文档

**发布流程：**

1. 自动运行所有平台的测试
2. 并行构建 4 个平台的可执行文件
3. 生成使用文档（USAGE.md）
4. 打包为压缩文件（Windows 使用 ZIP，其他使用 tar.gz）
5. 创建 GitHub Release（draft 状态）
6. 上传所有平台的压缩包

**查看发布：**

- 构建完成后，访问仓库的 **Releases** 页面
- 找到 draft release
- 检查所有平台的压缩包
- 如果一切正常，点击 **Publish release** 发布

**注意事项：**

- Release 默认创建为 **draft**（草稿）状态，需要手动发布
- 所有构建前会自动运行测试，确保代码质量
- 每个压缩包都包含完整的使用说明（USAGE.md）
- 工具数量：**83 个工具**（已移除 Python/UV/Pylance 工具）

**重要提醒：**

打包后的可执行文件**不包含** Python Development、UV Package Manager 和 Pylance/Pyright 工具，因为这些工具需要外部的 Python 解释器和相关工具。剩余的 83 个工具完全独立运行，无需任何外部依赖。
