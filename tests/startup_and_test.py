#!/usr/bin/env python3
"""
GW2日志评分系统 - 完整启动和验证脚本
功能：
1. 创建/管理虚拟环境
2. 安装依赖
3. 启动服务并验证
4. 执行功能测试
"""

import os
import sys
import socket
import http.client
import subprocess
import json

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_PATH = os.path.join(PROJECT_ROOT, "venv")
VENV_PYTHON = os.path.join(VENV_PATH, "Scripts", "python.exe") if os.name == 'nt' else os.path.join(VENV_PATH, "bin", "python")
VENV_PIP = os.path.join(VENV_PATH, "Scripts", "pip.exe") if os.name == 'nt' else os.path.join(VENV_PATH, "bin", "pip")

REQUIRED_PACKAGES = ["fastapi", "uvicorn", "python-multipart", "pandas", "openpyxl"]


def is_venv_valid():
    """检查虚拟环境是否有效"""
    return os.path.exists(VENV_PYTHON)


def create_venv():
    """创建虚拟环境"""
    print("[1/3] 创建虚拟环境...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True, cwd=PROJECT_ROOT)
        print("    [OK] 虚拟环境已创建: venv/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"    [FAIL] 虚拟环境创建失败: {e}")
        return False


def install_dependencies():
    """安装依赖包"""
    print("[2/3] 安装依赖包...")
    for pkg in REQUIRED_PACKAGES:
        print(f"    安装 {pkg}...", end=" ")
        try:
            subprocess.run([VENV_PIP, "install", pkg, "-q"], check=True, timeout=120)
            print("[OK]")
        except subprocess.TimeoutExpired:
            print("[超时]")
            return False
        except subprocess.CalledProcessError:
            print("[失败]")
            return False
    return True


def check_service(host, port, path="/api/logs"):
    """检查服务是否可用"""
    try:
        conn = http.client.HTTPConnection(host, port, timeout=3)
        conn.request("GET", path)
        resp = conn.getresponse()
        conn.close()
        return resp.status == 200
    except:
        return False


def start_server(port=8000):
    """启动服务器"""
    print("[3/3] 启动服务...")
    cmd = [VENV_PYTHON, "-m", "uvicorn", "src.core.application:app", "--host", "0.0.0.0", "--port", str(port)]
    proc = subprocess.Popen(cmd, cwd=PROJECT_ROOT)
    return proc


def verify_server(proc, port=8000, timeout=15):
    """验证服务器启动"""
    print("    等待服务响应...")
    for i in range(timeout):
        if check_service("localhost", port):
            print(f"    [OK] 服务已启动: http://localhost:{port}")
            print(f"    [OK] API文档: http://localhost:{port}/docs")
            return True
        import time
        time.sleep(1)
        if proc.poll() is not None:
            print("    [FAIL] 服务进程意外退出")
            return False
    print("    [FAIL] 服务启动超时")
    return False


def run_functional_tests():
    """运行功能测试"""
    print("\n" + "="*60)
    print("运行功能测试")
    print("="*60)

    tests_passed = 0
    tests_total = 0

    def test(name, condition, msg=""):
        nonlocal tests_passed, tests_total
        tests_total += 1
        if condition:
            tests_passed += 1
            print(f"    [PASS] {name}")
            return True
        else:
            print(f"    [FAIL] {name}: {msg}")
            return False

    conn = http.client.HTTPConnection("localhost", 8000, timeout=5)

    # API测试
    try:
        conn.request("GET", "/api/logs")
        resp = conn.getresponse()
        test("GET /api/logs", resp.status == 200)
        data = json.loads(resp.read().decode())
        test("Response format", "status" in data and "data" in data)
    except Exception as e:
        test("API endpoint", False, str(e))

    # 上传功能测试
    try:
        data_file = os.path.join(PROJECT_ROOT, "tests", "data.json")
        if os.path.exists(data_file):
            with open(data_file, 'rb') as f:
                content = f.read()

            from io import BytesIO
            from http.client import HTTPConnection

            conn.request("POST", "/api/upload",
                        body=content,
                        headers={"Content-Type": "application/octet-stream"})
            resp = conn.getresponse()
            result = json.loads(resp.read().decode())
            test("POST /api/upload", result.get("status") == "success", str(result))
    except Exception as e:
        test("Upload endpoint", False, str(e))

    conn.close()

    print(f"\n测试结果: {tests_passed}/{tests_total} 通过")
    return tests_passed == tests_total


def main():
    print("="*60)
    print("GW2日志评分系统 - 启动与验证")
    print("="*60)
    print()

    # 检查虚拟环境
    if not is_venv_valid():
        print("[INFO] 未检测到虚拟环境，正在创建...")
        if not create_venv():
            sys.exit(1)
        if not install_dependencies():
            sys.exit(1)
    else:
        print("[INFO] 虚拟环境已存在")

    # 启动服务
    proc = start_server()
    if not verify_server(proc):
        proc.terminate()
        sys.exit(1)

    # 运行测试
    success = run_functional_tests()

    # 保持服务运行
    print("\n" + "="*60)
    if success:
        print("系统状态: 正常运行")
    else:
        print("系统状态: 部分功能异常 - 请检查上述失败测试")
    print("="*60)
    print("\n按 Ctrl+C 停止服务")

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("\n服务已停止")


if __name__ == "__main__":
    main()
