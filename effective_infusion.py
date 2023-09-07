import pandas as pd
from datetime import timedelta
import os    #加载操作系统模块
from utils import recursive_walk_files_only
#获取有效输注次数
def get_csv_effective_infusion_times(path):
    # 读取csv文件
    df = pd.read_csv(path)
    # 要求1：筛选"事件名称"栏为"停止输注"或"启动速度模式"的列
    df = df[df['事件名称'].isin(['停止输注\t', '启动速度模式\t'])]
    # 将"时间"栏转换为datetime类型
    df['时间'] = pd.to_datetime(df['时间'])
    # 创建一个新列，该列为下一行的"时间"，这样我们可以计算时间间隔
    df['下一时间'] = df['时间'].shift(-1)
    df['有效输注时间'] = df['时间'] - df['下一时间']
    ret = (df['事件名称'].str.contains('停止输注')) & (df['有效输注时间'] > timedelta(minutes=1))
    # 要求2：在要求1筛选后的数据中筛选:从事件"启动速度模式"到事件"停止输注"之间时间间隔大于1分钟的列
    df = df[ret]
    # 要求3：统计在符合要求2的列中，"事件名称"栏为"启动速度模式"的列数量
    return df.shape[0]
#获取有效输注次数
def get_xlsx_effective_infusion_times(path):
    # 读取xls（绝对路径）
    df = pd.read_excel(path)
    # 要求1：筛选"事件名称"栏为"停止输注"或"启动速度模式"的列
    df = df[df['事件'].isin(['停止输注', '启动输注'])]
    # 将"时间"栏转换为datetime类型
    df['时间'] = pd.to_datetime(df['时间'], format="%Y年%m月%d日 %H时%M分%S秒")
    # 创建一个新列，该列为下一行的"时间"，这样我们可以计算时间间隔
    df['下一时间'] = df['时间'].shift(-1)
    df['有效输注时间'] = df['下一时间']- df['时间']
    ret = (df['事件'].str.contains('启动输注')) & (df['有效输注时间'] > timedelta(minutes=1))
    # 要求2：在要求1筛选后的数据中筛选:从事件"启动速度模式"到事件"停止输注"之间时间间隔大于1分钟的列
    df = df[ret]
    # 要求3：统计在符合要求2的列中，"事件名称"栏为"启动速度模式"的列数量
    return df.shape[0]

def cal_effective_infusion_times_in_dir(dir):
    for path in recursive_walk_files_only(dir):   
        if path.endswith('.csv') and '次' not in path:
            count = get_csv_effective_infusion_times(path)
            os.rename(path,path.replace('.csv','')+'-有效输注'+str(count)+'次'+'.csv')
        elif path.endswith('.xlsx') and '次' not in path:
            count = get_xlsx_effective_infusion_times(path)
            os.rename(path,path.replace('.xlsx','')+'-有效输注'+str(count)+'次'+'.xlsx')
        print(path)