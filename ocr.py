#!/usr/bin/python
#-*-coding:utf-8 -*-
#pip install baidu-aip
#pip install requests PyPDF2 reportlab
from tkinter import *
from tkinter import filedialog
import tkinter as tk
import os    #加载操作系统模块
from aip import AipOcr    #调用百度Ocr模块
import requests    #调用反馈模块
import time    #调用时间模块
import re
import pandas as pd
# 读取文件
def get_file_content(filePath):
     with open(filePath, 'rb') as fp:
            return fp.read()
# 文件下载函数
def file_download(url, file_path):
    print(url)
    r = requests.get(url)
    with open(file_path, 'wb') as f:
            f.write(r.content)
# 添加诊断
def addDiagnose(form, data):
    ret = ''
    if re.search('[\u4e00-\u9fa5]', data) is None or data.isdigit():
        ret = str(form)
    elif isinstance(form, str) and ('nan' in form or data in form):
        ret = data
    else:
        ret = str(form) + '\n' + data
    return ret.replace("nan", "")
# 添加ID
def addCode(form,data):
    ret = ''
    if 'nan' in str(form) or data in str(form):
        ret = data
    else:
        ret = str(form) + '\n' + data
    return ret.replace("nan", "")
# 增强识别功能
def enhancedRecognition(path):
    f = open(path,"r",encoding='gb18030')  
    lines = f.readlines()
    df = pd.DataFrame(index=range(50), columns=['Diagnose', 'ID', 'Advise','Age','Gender','Time','Code'])
    index = 0
    gap = 0
    #上一行内容 
    previous_data = ''
    for data in lines:
        data = data.strip()
        #过滤无用数据
        if '…' in data:
            continue
        ##时间格式：2023-02-24 06:32:.
        if 2 == data.count(":"):
            if re.search(r"\d{4}-\d{2}-\d{2}$",data):
                df['Time'][index] = data
            elif re.search(r"\d{4}-\d{2}-\d{2}$",previous_data):
                df['Time'][index] = previous_data + data
            else:   
                df['Time'][index] = data
        #年龄后面添加岁
        elif '岁' in data:
            if re.fullmatch(r"\d+岁", data):
                df['Age'][index] = data
            else:
                result = re.search(r"\d+岁", data)
                if result != None:
                    age = result.group()
                    previous_data = data.split(age)[0]
                    df['Age'][index] = age
            #医嘱是中文，或者3个大写的英文缩写
            if re.search('[\u4e00-\u9fa5]', previous_data) or re.match("[A-Z]{3}",previous_data) != None:
                df['Advise'][index] = previous_data
        elif '男' in data or '女' in data:
            df['Gender'][index] = data
        elif re.fullmatch(r'\d{10}', data):
            df['Code'][index] = addCode(df['Code'][index],data)
        elif re.fullmatch(r'\d{5,8}', data):
            df['ID'][index] = data 
            df['Diagnose'][index] = addDiagnose(df['Diagnose'][index],previous_data)
            index += 1
        #匹配序号
        elif re.fullmatch(r'\d{1,3}', previous_data):
            if 0 == gap:
                gap = int(previous_data) - index
            else:
                if int(previous_data) - gap == (index + 1):
                    index += 1
            df['Diagnose'][index] = addDiagnose(df['Diagnose'][index],data)
        previous_data = data
    df.to_csv(path+'.csv',encoding='gb18030')
    f.close()
    ##删除txt文件
    os.remove(path)
# 表格识别功能
def formImageOCR(client,imagePath):
    if False == os.path.isfile(imagePath):
        print('文件路径错误：'+imagePath)
        return
    print('正在处理：'+imagePath)
    image = get_file_content(imagePath)    #调用读取图片子程序
    res = client.tableRecognitionAsync(image)    #调用表格文字识别
    #报错下一个
    if None == res.get('result'):
        print('转换失败：'+res['error_msg'])
        return
    req_id = res['result'][0]['request_id']    #获取识别ID号
    
    for count in range(1,10):    #OCR识别也需要一定时间，设定10秒内每隔1秒查询一次
        res = client.getTableRecognitionResult(req_id)    #通过ID获取表格文件XLS地址
        #报错下一个
        if None == res.get('result') or '异常' in res['result']['ret_msg']:
            print('转换失败：')
            return
        print(res['result']['ret_msg'])
        if res['result']['ret_msg'] == '已完成':
            break    #云端处理完毕，成功获取表格文件下载地址，跳出循环
        else:
            time.sleep(3) 
    url = res['result']['result_data']
    xlsPath = imagePath + '.xls'
    file_download(url, xlsPath)    #调用文件下载子程序
    print("完成转换,表格输出路径为:"+xlsPath)
    time.sleep(1)
# 高精度文字识别功能
def accurateImageOCR(client,imageFilePath,enchance = False):
    if False == os.path.isfile(imageFilePath):
        print('文件路径错误：'+imageFilePath)
        return
    print('正在处理：'+imageFilePath)
    image=get_file_content(imageFilePath)
    #接通ocr接口
    result=client.basicAccurate(image)
    #报错下一个
    if None == result.get('words_result'):
        print('转换失败：'+ result['error_msg'])
        return
    mywords=result["words_result"]
    txtPath = imageFilePath+".txt"
    f = open(txtPath,'w',encoding='GB18030')
    for i in range(len(mywords)):
        f.write(mywords[i]["words"]+"\n")
    f.close()
    print("完成转换,txt输出路径为:"+txtPath)
    ##删除img文件
    os.remove(imageFilePath)
    if enchance:
        enhancedRecognition(txtPath)