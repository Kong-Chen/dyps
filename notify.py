import requests

def send_line_notify(message, token):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': 'Bearer ' + token
    }
    data = {
        'message': message
    }
    response = requests.post(url, headers=headers, data=data)
    return response

# 使用範例
#token = 'PPb8rGTHk5j1Bz3YaGiDVGlJ1qQAxsyqYs7etGKVMAV' #Kong
token = 'RJhGOMUMHuvBGXM8vpi5IgoGuNLREF7bwKx6heTTQLK' #Group
message = '測試一下！'
response = send_line_notify(message, token)
print(response.text)