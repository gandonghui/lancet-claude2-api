import requests
import json

class AskYourPDF:
    def __init__(self, api_key):
        self.api_key = api_key

    def generate_source_id_base_url(self, url):
        ret = ''
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        data = {'url': url}
        response = requests.post('https://api.chatpdf.com/v1/sources/add-url', headers=headers, json=data)
        if response.status_code == 200:
            ret = response.json()['sourceId']
            print('Source ID:', ret)
        else:
            print('Status:', response.status_code)
            print('generate_source_id_base_url Error:', response.text)
        return ret

    def generate_source_id_base_local_pdf(self, local_pdf_path):
        ret = ''         
        headers = {
        'x-api-key': self.api_key
        }
        file_data = open(local_pdf_path, 'rb')
        response = requests.post('https://api.askyourpdf.com/v1/api/upload', headers=headers,files={'file': file_data})
        if response.status_code == 201:
            ret = response.json()['docId']
            print(ret)
        else:
            print('Error:', response.status_code)
        return ret

    def chat_base_prompt(self, source_id, prompt):
        ret = ''
        headers = {
        'Content-Type': 'application/json',
        'x-api-key': self.api_key
        }

        data = [
        {
        "sender": "User",
        "message": prompt
        }
        ]

        response = requests.post(f'https://api.askyourpdf.com/v1/chat/{source_id}', 
        headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            ret = response.json()['answer']['message']
        else:
            print('Error:', response.status_code)
        return ret

    def delete_source_id(self, source_id):
        headers = {
        'x-api-key': self.api_key
        }
        response = requests.delete(f'https://api.askyourpdf.com/v1/api/documents/{source_id}', headers=headers)

        if response.status_code == 200:
            print('Document deleted successfully')
        else:
            print('Error:', response.status_code)

