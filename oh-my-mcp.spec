# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('.venv\\Lib\\site-packages\\fastmcp-2.14.5.dist-info', 'fastmcp-2.14.5.dist-info'), ('.venv\\Lib\\site-packages\\fakeredis\\commands.json', 'fakeredis'), ('D:\\Developments\\mcp-server\\src\\mcp_server\\tools\\compression\\config.yaml', 'mcp_server\\tools\\compression'), ('D:\\Developments\\mcp-server\\src\\mcp_server\\tools\\data\\config.yaml', 'mcp_server\\tools\\data'), ('D:\\Developments\\mcp-server\\src\\mcp_server\\tools\\file\\config.yaml', 'mcp_server\\tools\\file'), ('D:\\Developments\\mcp-server\\src\\mcp_server\\tools\\subagent\\config.yaml', 'mcp_server\\tools\\subagent'), ('D:\\Developments\\mcp-server\\src\\mcp_server\\tools\\system\\config.yaml', 'mcp_server\\tools\\system'), ('D:\\Developments\\mcp-server\\src\\mcp_server\\tools\\text\\config.yaml', 'mcp_server\\tools\\text'), ('D:\\Developments\\mcp-server\\src\\mcp_server\\tools\\utility\\config.yaml', 'mcp_server\\tools\\utility'), ('D:\\Developments\\mcp-server\\src\\mcp_server\\tools\\web\\config.yaml', 'mcp_server\\tools\\web')]
binaries = []
hiddenimports = ['mcp_server.tools.compression', 'mcp_server.tools.compression.handlers', 'mcp_server.tools.web', 'mcp_server.tools.web.handlers', 'mcp_server.tools.file', 'mcp_server.tools.file.handlers', 'mcp_server.tools.data', 'mcp_server.tools.data.handlers', 'mcp_server.tools.text', 'mcp_server.tools.text.handlers', 'mcp_server.tools.system', 'mcp_server.tools.system.handlers', 'mcp_server.tools.utility', 'mcp_server.tools.utility.handlers', 'mcp_server.tools.subagent', 'mcp_server.tools.subagent.handlers', 'mcp_server.tools.subagent_config', 'mcp_server.tools.search_engine', 'mcp_server.tools.registry', 'mcp_server.utils', 'mcp_server.command_executor', 'mcp_server.cli', 'mcp_server.cli.config', 'psutil', 'yaml', 'lxml', 'lxml.etree', 'lxml.html', 'bs4', 'requests', 'urllib3', 'ddgs', 'dateutil']
tmp_ret = collect_all('fastmcp')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('mcp')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('httpx')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('uvicorn')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('websockets')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pydantic')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pydantic_core')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('rich')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('anyio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('authlib')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('cyclopts')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('jsonref')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('jsonschema_path')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('openapi_pydantic')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pydocket')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('fakeredis')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('lupa')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('sniffio')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['src\\mcp_server\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'PIL', 'IPython', 'jupyter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='oh-my-mcp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='oh-my-mcp',
)
