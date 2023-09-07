import os
from googletrans import Translator
import pandas as pd
import numpy as np
import re
import pdfplumber
import sys

#sys.stdout.encoding = 'gb18030'

def pdf_to_text(path):
    text = ''
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text+=page.extract_text()
    return text

def recursive_walk_files_only(dir_path):
    ret = []
    for root, _, files in os.walk(dir_path):
        for file in files:
            path = os.path.join(root, file)
            # Normalize the path and replace backslashes with slashes
            path = os.path.normpath(path)   
            ret.append(path)
    return ret

def translate(text, src_lang, dest_lang):
    ret = ''
    if '' != text:
        translator = Translator(service_urls=['translate.google.com'],raise_exception=True)
        ret = translator.translate (text, src=src_lang, dest=dest_lang).text
    return ret

def translate_data(data, target_language):
    translator = Translator()

    translated_data = []
    for sublist in data:
        translated_sublist = [translator.translate(item, dest=target_language).text for item in sublist]
        translated_data.append(translated_sublist)
    return translated_data
    
# Function to check if the list contains nested lists
def has_nested_list(lst):
    return any(isinstance(item, list) for item in lst)

# Function to fully flatten the nested list
def flatten_list(nested_list):
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten_list(item)
        else:
            yield item


def to_excel(columns, data, path):
    data = [
        [item.tolist() if isinstance(item, np.ndarray) else item for item in sublist]
        for sublist in data
    ]
    #去除嵌套
    data = [item for sublist in data for item in sublist]
    # Check if the 'data' list contains nested lists
    if has_nested_list(data):
        # Flatten the nested lists before processing
        flattened_data = [list(flatten_list(item)) for item in data]
    else:
        flattened_data = data
    # Find the length of the longest list
    max_len = max(len(d) for d in flattened_data)
    # Pad the smaller lists with None to match the length of the longest list
    data_padded = [d + [None] * (max_len - len(d)) for d in flattened_data]
    # translate
    data = translate_data(data_padded, 'zh-cn')
    # Create the DataFrame
    print(data)
    df = pd.DataFrame(data, columns=columns)
    # Replace None with empty strings
    df = df.fillna('')
    df.to_excel(path, index=False)

def get_sn_from_path(path):
    sn_number = ''
    pattern = r'SN-([A-Za-z0-9]+)'
    match = re.search(pattern, path)
    if match:
        sn_number = match.group(1)
    return sn_number

def xlsx_to_csv(excel_file):
    ret = []
    dir = os.path.dirname(excel_file)
    with pd.ExcelFile(excel_file,engine='openpyxl') as xls:
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name,engine='openpyxl')
            csv_file_name = f'{sheet_name.replace(" ", "_").replace("/", "_")}.csv'
            file_path = os.path.join(dir, csv_file_name)
            df.to_csv(file_path, index=False)
            ret.append(file_path)
    return ret
    
def markdown_to_csv(markdown,csv_path):
    header_match = re.search(r'\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|', markdown)
    if header_match:
        header = [cell.strip() for cell in header_match.groups()]
    else:
        return
    pattern = r'\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|'
    matches = re.findall(pattern, markdown)
    df = pd.DataFrame(matches, columns=header)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df.to_csv(csv_path, index=False)