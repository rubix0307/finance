import requests


for i in range(15):
    requests.get('http://127.0.0.1:8012/process_receipt_view/')

if __name__ == '__main__':
    pass