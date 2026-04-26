#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件上传功能
"""

import requests
import os

# 测试文件路径
test_file_path = "tests/data/20260408-222901.zevtc"
# API端点
api_url = "http://localhost:8001/api/upload"

print(f"Testing file upload with: {test_file_path}")
print(f"API endpoint: {api_url}")

if not os.path.exists(test_file_path):
    print(f"Error: Test file not found at {test_file_path}")
    exit(1)

# 发送文件上传请求
try:
    with open(test_file_path, 'rb') as f:
        files = {'file': (os.path.basename(test_file_path), f)}
        response = requests.post(api_url, files=files)
    
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
    
    if response.status_code == 200:
        print("✅ File upload successful!")
    else:
        print("❌ File upload failed!")
        
except Exception as e:
    print(f"Error uploading file: {e}")
