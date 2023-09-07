import requests
import re

class ChatPDF:
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
        files = [
            ('file', ('file', open(local_pdf_path, 'rb'), 'application/octet-stream'))
        ]
        headers = {
            'x-api-key': self.api_key
        }
        response = requests.post('https://api.chatpdf.com/v1/sources/add-file', headers=headers, files=files)
        if response.status_code == 200:
            ret = response.json()['sourceId']
            print('Source ID:', ret)
        else:
            print('Status:', response.status_code)
            print('generate_source_id_base_local_pdf Error:', response.text)
        return ret

    def chat_base_prompt(self, source_id, prompt):
        ret = ''
        headers = {
            'x-api-key': self.api_key,
            "Content-Type": "application/json",
        }
        data = {
            'referenceSources': True,
            'sourceId': source_id,
            'messages': [
                {
                    'role': "user",
                    'content': prompt,         
                }]
        }
        response = requests.post('https://api.chatpdf.com/v1/chats/message', headers=headers, json=data)
        if response.status_code == 200:
            ret = response.json()['content']
        else:
            print('Status:', response.status_code)
            print('chat_base_prompt Error:', response.text)
        return ret

    def delete_source_id(self, source_id):
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json',
        }
        data = {
            'sources': [source_id],
        }
        try:
            response = requests.post('https://api.chatpdf.com/v1/sources/delete', json=data, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as error:
            print('delete_source_id Error:', error)
            print('Response:', error.response.text)
