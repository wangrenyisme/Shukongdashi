#将word中的数据转换，进行拆分，存到mysql
# -*- coding: utf-8 -*-
import re
import pandas as pd

with open('data.txt', 'r',encoding='utf-8') as f:
    lines = f.readlines()
guzhangyuanyin = []
guzhangxianxiang = []
guzhangfenxi = []
for i,line in enumerate(lines):
    if line.startswith('例') and '故障现象' not in line:
        yuanyin = ''
        try:
            yuanyin = line.split('.')[1].strip().replace('维修','')
        except:
            print(i,i)
        j = i + 1

        if lines[j].startswith('故障现象'):
            guzhangyuanyin.append(yuanyin)
            print(i, yuanyin)
            xianxiang = ''
            while not lines[j].startswith('分析'):
                if lines[j].strip() != '':
                    xianxiang = xianxiang + lines[j]
                j = j + 1
            xianxiang = re.split('故障现象:|故障现象：|故障现象;|故障现象',xianxiang)[1].replace('\n','')
            guzhangxianxiang.append(xianxiang)
            print(i,xianxiang)
        if lines[j].startswith('分析'):
            fenxi = ''
            while j < len(lines) and not lines[j].startswith('例'):
                if lines[j].strip() != '' and '故障维修' not in lines[j]:
                    fenxi = fenxi +lines[j]
                j = j + 1
            fenxi = re.split('过程:|过程：|过程;|过程；',fenxi)[1]
            guzhangfenxi.append(fenxi)
            print(i,fenxi)
        else:
            while(lines[j].startswith('例') and '故障现象' in lines[j]):
                guzhangyuanyin.append(yuanyin)
                print(i,yuanyin)
                if '故障现象' in lines[j]:
                    xianxiang = ''
                    while not lines[j].startswith('分析'):
                        if lines[j].strip() != '':
                            xianxiang = xianxiang + lines[j]
                        j = j + 1
                    xianxiang = re.split('故障现象:|故障现象：|故障现象;|故障现象',xianxiang)[1].replace('\n','')
                    guzhangxianxiang.append(xianxiang)
                    print(i,xianxiang)
                if lines[j].startswith('分析'):
                    fenxi = ''
                    while not lines[j].startswith('例'):
                        if lines[j].strip() != '' and '故障维修' not in lines[j]:
                            fenxi = fenxi +lines[j]
                        j = j + 1
                    fenxi = re.split('过程:|过程：|过程;|过程；',fenxi)[1]
                    guzhangfenxi.append(fenxi)
                    print(i,fenxi)
result = pd.DataFrame()
# result['guzhangyuanyin'] = guzhangyuanyin
result['guzhangxianxiang'] = guzhangxianxiang
# result['guzhangfenxi'] = guzhangfenxi
result.to_csv('guzhangxianxiang.csv', index=None,encoding='utf-8')
print(len(guzhangyuanyin),len(guzhangxianxiang),len(guzhangfenxi))