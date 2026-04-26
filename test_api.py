import requests

# 测试获取字典分组API
response = requests.get('http://localhost:8000/api/dict/groups')
print('Response status code:', response.status_code)
print('Response headers:', response.headers)
print('Response encoding:', response.encoding)
print('Response text:', response.text)

# 测试初始化字典数据API
response = requests.post('http://localhost:8000/api/dict/initialize')
print('\nInitialize response status code:', response.status_code)
print('Initialize response headers:', response.headers)
print('Initialize response encoding:', response.encoding)
print('Initialize response text:', response.text)
