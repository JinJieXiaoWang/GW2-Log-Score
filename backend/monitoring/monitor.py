#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控脚本

用于实时监测服务器的运行状态、端口占用情况、内存使用、CPU负载等关键指标
"""

import os
import sys
import time
import psutil
import socket
import logging
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)), 'logs', 'monitor.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """系统监控类"""

    def __init__(self, check_interval=60):
        """
        初始化监控器

        Args:
            check_interval: 检查间隔（秒）
        """
        self.check_interval = check_interval
        self.monitoring_data = []

    def check_port(self, port):
        """
        检查端口是否被占用

        Args:
            port: 端口号

        Returns:
            bool: 端口是否被占用
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.error(f"Error checking port {port}: {e}")
            return False

    def get_system_metrics(self):
        """
        获取系统指标

        Returns:
            dict: 系统指标
        """
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_used = memory.used / (1024 ** 3)  # 转换为 GB
            memory_total = memory.total / (1024 ** 3)  # 转换为 GB
            memory_percent = memory.percent

            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            disk_used = disk.used / (1024 ** 3)  # 转换为 GB
            disk_total = disk.total / (1024 ** 3)  # 转换为 GB
            disk_percent = disk.percent

            # 网络情况
            net_io = psutil.net_io_counters()
            bytes_sent = net_io.bytes_sent / (1024 ** 2)  # 转换为 MB
            bytes_recv = net_io.bytes_recv / (1024 ** 2)  # 转换为 MB

            # 进程情况
            process_count = len(psutil.pids())

            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent
                },
                'memory': {
                    'used': round(memory_used, 2),
                    'total': round(memory_total, 2),
                    'percent': memory_percent
                },
                'disk': {
                    'used': round(disk_used, 2),
                    'total': round(disk_total, 2),
                    'percent': disk_percent
                },
                'network': {
                    'bytes_sent': round(bytes_sent, 2),
                    'bytes_recv': round(bytes_recv, 2)
                },
                'processes': process_count
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    def check_service_status(self):
        """
        检查服务状态

        Returns:
            dict: 服务状态
        """
        try:
            # 检查后端服务端口
            backend_port = 8001
            backend_running = self.check_port(backend_port)

            # 检查数据库文件是否存在
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)), 'database', 'gw2_logs.db'))
            db_exists = os.path.exists(db_path)

            # 检查上传目录是否存在
            upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)), 'uploads'))
            upload_dir_exists = os.path.exists(upload_dir)

            return {
                'backend': {
                    'running': backend_running,
                    'port': backend_port
                },
                'database': {
                    'exists': db_exists,
                    'path': db_path
                },
                'upload_dir': {
                    'exists': upload_dir_exists,
                    'path': upload_dir
                }
            }
        except Exception as e:
            logger.error(f"Error checking service status: {e}")
            return {
                'error': str(e)
            }

    def run(self):
        """
        运行监控
        """
        logger.info("Starting system monitor...")
        
        while True:
            try:
                # 获取系统指标
                system_metrics = self.get_system_metrics()
                
                # 检查服务状态
                service_status = self.check_service_status()
                
                # 合并监控数据
                monitoring_data = {
                    'system': system_metrics,
                    'services': service_status
                }
                
                # 记录监控数据
                self.monitoring_data.append(monitoring_data)
                
                # 限制监控数据长度
                if len(self.monitoring_data) > 100:
                    self.monitoring_data.pop(0)
                
                # 保存监控数据到文件
                self.save_monitoring_data()
                
                # 记录日志
                self.log_monitoring_data(monitoring_data)
                
                # 检查是否有异常
                self.check_for_anomalies(monitoring_data)
                
                # 等待下一次检查
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)

    def save_monitoring_data(self):
        """
        保存监控数据到文件
        """
        try:
            data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)), 'logs', 'monitoring_data.json')
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.monitoring_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving monitoring data: {e}")

    def log_monitoring_data(self, data):
        """
        记录监控数据到日志

        Args:
            data: 监控数据
        """
        try:
            # 简化日志输出
            log_data = {
                'timestamp': data['system']['timestamp'],
                'cpu_percent': data['system']['cpu']['percent'],
                'memory_percent': data['system']['memory']['percent'],
                'disk_percent': data['system']['disk']['percent'],
                'backend_running': data['services']['backend']['running'],
                'db_exists': data['services']['database']['exists']
            }
            logger.info(f"Monitoring data: {json.dumps(log_data, ensure_ascii=False)}")
        except Exception as e:
            logger.error(f"Error logging monitoring data: {e}")

    def check_for_anomalies(self, data):
        """
        检查异常情况

        Args:
            data: 监控数据
        """
        try:
            # 检查CPU使用率
            cpu_percent = data['system']['cpu']['percent']
            if cpu_percent > 80:
                logger.warning(f"High CPU usage: {cpu_percent}%")

            # 检查内存使用率
            memory_percent = data['system']['memory']['percent']
            if memory_percent > 80:
                logger.warning(f"High memory usage: {memory_percent}%")

            # 检查磁盘使用率
            disk_percent = data['system']['disk']['percent']
            if disk_percent > 80:
                logger.warning(f"High disk usage: {disk_percent}%")

            # 检查后端服务状态
            if not data['services']['backend']['running']:
                logger.warning("Backend service is not running")

            # 检查数据库文件
            if not data['services']['database']['exists']:
                logger.warning("Database file does not exist")

            # 检查上传目录
            if not data['services']['upload_dir']['exists']:
                logger.warning("Upload directory does not exist")

        except Exception as e:
            logger.error(f"Error checking for anomalies: {e}")

if __name__ == "__main__":
    # 创建监控器实例
    monitor = SystemMonitor(check_interval=60)  # 每分钟检查一次
    
    # 运行监控
    monitor.run()