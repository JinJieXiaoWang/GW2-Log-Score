#!/usr/bin/env python3
"""
GW2日志评分系统 - 带启动验证的启动脚本
"""

import os
import sys
import argparse
import time
import socket
import http.client
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.logger import Logger

logger = Logger(__name__)

def check_port_available(host, port):
    """检查端口是否可用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex((host, port))
        sock.close()
        return result != 0
    except:
        return False

def wait_for_service(host, port, timeout=30):
    """等待服务启动"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            conn = http.client.HTTPConnection(host, port, timeout=2)
            conn.request("GET", "/api/logs")
            response = conn.getresponse()
            conn.close()
            return True
        except:
            time.sleep(0.5)
            continue
    return False

def main():
    parser = argparse.ArgumentParser(description="GW2日志解析与出勤评分系统")
    parser.add_argument("--dir", help="指定待解析日志所在的文件夹路径")
    parser.add_argument("--file", help="指定单个待解析日志文件路径")
    parser.add_argument("--export", help="导出全量历史评分报表 (CSV路径)")
    parser.add_argument("--db", default="databases/gw2_logs.db", help="指定数据库文件路径")
    parser.add_argument("--serve", action="store_true", help="启动FastAPI服务器")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", default=8000, type=int, help="服务器端口")

    args = parser.parse_args()

    if args.serve:
        from src.config import HOST, PORT

        actual_host = args.host or HOST
        actual_port = args.port or PORT

        if not check_port_available(actual_host, actual_port):
            logger.error(f"端口 {actual_port} 已被占用，请先停止占用该端口的进程或使用其他端口")
            sys.exit(1)

        logger.info(f"启动后端服务...")
        logger.info(f"服务将在 http://{actual_host}:{actual_port} 上运行")
        logger.info(f"按 Ctrl+C 停止服务")

        import uvicorn
        server_config = uvicorn.Config(
            "src.core.application:app",
            host=actual_host,
            port=actual_port,
            log_level="info"
        )
        server = uvicorn.Server(server_config)

        import threading
        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()

        logger.info("等待服务启动...")
        time.sleep(2)

        if wait_for_service(actual_host, actual_port, timeout=10):
            logger.info("=" * 50)
            logger.info("服务启动成功！")
            logger.info(f"API文档地址: http://localhost:{actual_port}/docs")
            logger.info("=" * 50)
            logger.info("按 Ctrl+C 停止服务")

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("正在停止服务...")
                sys.exit(0)
        else:
            logger.error("服务启动失败，请检查日志中的错误信息")
            sys.exit(1)

    else:
        from src.main import App
        app = App(args.db)

        if args.file:
            app.process_file(args.file)
        elif args.dir:
            app.process_folder(args.dir)
        elif args.export:
            app.export_report(args.export)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
