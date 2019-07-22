#对故障现象进行分析，分词，抽取出故障部位，故障现象，故障发生的背景
#encoding=utf-8
import re
import jieba
import pandas as pd

def chaifenxianxiang():
    readed_data = pd.read_csv("guzhangxianxiang.csv")
    xianxianglist = readed_data['guzhangxianxiang'].tolist()
    fen_xianxianglist = []
    f = open('biaozhu.txt','w+',encoding='utf-8')
    for xianxiang in xianxianglist:
        xianxiang = xianxiang.replace(' ','').replace('（','').replace('）','').replace('“','').replace('”','').replace('？','')
        pattern = r',|\.|;|\?|:|!|，|。|；|！'
        # data = '/ '.join(re.split(pattern,xianxiang))
        # print(data)
        xianlist = re.split(pattern, xianxiang)
        for x in xianlist:
            if x.strip() !='':
                f.write('\t'+x+'\n')
    f.close()
        # data = ''.join(re.findall(u'[0-9a-zA-Z\u4e00-\u9fa5]+', xianxiang))
        # seg_list = jieba.cut(data, cut_all=False)
        #
        # print("Default Mode:", "/".join(seg_list))  # 精确模式
    return

def biaozhu_mingming():
    fw = open('biaozhu_minming.txt','w+',encoding='utf-8')
    with open('biaozhu.txt', 'r',encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        biaozhu = line.split('\t')[0]
        data = line.split('\t')[1]
        if biaozhu == '1':
            fw.write('机床类型\t'+data)
        elif biaozhu == '2':
            fw.write('执行操作\t' + data)
        elif biaozhu == '3':
            fw.write('故障现象\t' + data)
    fw.close()
    return

if __name__ == '__main__':
    biaozhu_mingming()