#根据标注好的数据进行训练之后，可以预测描述的类型，根据不同的类型，按照不同的方式拆分
#encoding=utf-8
import re
import pymysql
import pandas as pd
from itertools import combinations
# import thulac
# import jieba
import jieba.analyse
import jieba.posseg
from Shukongdashi.test_my.test_cnnrnn.predict import CnnModel
db = pymysql.connect(host='localhost', user='root', password='root', db='sg_faq')
cursor = db.cursor()  # 获取指针以操作数据库
cursor.execute('set names utf8')
yuanyindb = []
xianxaingdb = []
sql = 'select guzhangyuanyin, guzhangxianxiang FROM guzhanganli'
try:
    # 执行SQL语句
    cursor.execute(sql)
    # 获取所有记录列表
    results = cursor.fetchall()
    for row in results:
        yuanyindb.append(row[0])
        xianxaingdb.append(row[1])
except:
    print("Error: unable to fetch data")
# 关闭数据库连接
db.close()
# miaoshu = '一台配套FANUC 6M的加工中心,在机床搬迁后，首次开机时，机床出现 剧烈振动，CRT显示401、430报警。'
# miaoshu ='一台配套FANUC 6ME系统的加工中心，由于伺服电动机损伤，在 更换了 X轴伺服电动机后，机床一接通电源,X轴电动机即高速转动,CNC发生ALM410 报警并停机。'
# miaoshu ='某配套PLASMA系统的5轴加工中心，在加工过程中，机床突然出现X、 Y、Z轴同时快速运动，导致机床碰撞，引起刀具与工件的损坏。'
# miaoshu = miaoshu.replace(' ','').replace('（','').replace('）','').replace('“','').replace('”','').replace('？','')
#拆分成句子
jieba.load_userdict('fencidian.txt')
pattern = r'\.|;|。|；|！'
pattern2 = r',|，'
cnn_model = CnnModel()
zhuyu_list = []
baojing_list = []
caozuo_list = []
xianxiang_list = []
#保存关系
#操作和现象
caozuo_title = []
xianxiang_caozuo_title = []
#现象和原因之间
xianxiang_yuanyin_title = []
yuanyin_title = []
#现象之间的关联
xianxiang_title1 = []
xianxiang_title2 = []
#部位和报警和现象之间的关联
buwei_xianxiang_title = []
xianxaing_buwei_title = []
baojing_xianxiang_title = []
xianxaing_baojing_title = []

#加载停用词
stopwords = []
with open('stopwords.txt', 'r', encoding='utf-8') as f:
    st = f.readlines()
for line in st:
    line = line.strip().encode('utf-8').decode('utf-8-sig')
    stopwords.append(line)
#加载故障部位
buweizhuyu = []
with open('zhuyu.txt', 'r', encoding='utf-8') as f:
    st = f.readlines()
for line in st:
    line = line.strip().encode('utf-8').decode('utf-8-sig')#防止BOM现象
    buweizhuyu.append(line)

# thu_lac = thulac.thulac(user_dict='fencidian.txt')  # 默认模式
for i,miaoshu in enumerate(xianxaingdb):
    miaoshu = miaoshu.replace(' ', '')
    print(u'正在过滤停用词......')
    miaoshu_baocun = []
    miaoshu_cut = jieba.cut(miaoshu)
    for m in miaoshu_cut:
        if m not in stopwords:
            miaoshu_baocun.append(m)
    miaoshu = ''.join(miaoshu_baocun)

    miaoshu_jvzi = re.split(pattern, miaoshu)
    miaoshu_jvzi = list(filter(None, miaoshu_jvzi))
    #保存描述中描述品牌型号、执行操作、报警现象的内容
    miaoshu_xinghao = []
    miaoshu_caozuo = []
    miaoshu_xianxiang = []
    for jvzi in miaoshu_jvzi:
        #把句子进一步拆分
        miaoshu_list = re.split(pattern2, jvzi)
        miaoshu_list = list(filter(None, miaoshu_list))
        #判断类型,把相同的类型放到一起
        for miaoshu in miaoshu_list:
            miaoshu_type = cnn_model.predict(miaoshu)
            if miaoshu_type == '机床类型':
                miaoshu_xinghao.append(miaoshu)
            elif miaoshu_type == '执行操作':
                if miaoshu not in caozuo_list:
                    caozuo_list.append(miaoshu)
                miaoshu_caozuo.append(miaoshu)
            elif miaoshu_type == '故障现象':
                if miaoshu not in xianxiang_list:
                    xianxiang_list.append(miaoshu)
                miaoshu_xianxiang.append(miaoshu)
    #初始化操作和故障，故障和原因之间的关系
    for xianxiang in miaoshu_xianxiang:
        for caozuo in miaoshu_caozuo:
            caozuo_title.append(caozuo)
            xianxiang_caozuo_title.append(xianxiang)
        xianxiang_yuanyin_title.append(xianxiang)
        yuanyin_title.append(yuanyindb[i])
    #故障现象之间的关联关系
    zuhe_xianxiaing = list(combinations(miaoshu_xianxiang, 2))
    for zuhe in zuhe_xianxiaing:
        xianxiang_title1.append(zuhe[0])
        xianxiang_title2.append(zuhe[1])
        xianxiang_title1.append(zuhe[1])
        xianxiang_title2.append(zuhe[0])
    #到此，不同的描述放到了不同的list里
    #处理品牌型号描述
    miaoshu_xinghao = ''.join(miaoshu_xinghao)
    pinpai_xinghao = ''.join(re.findall(u'[0-9a-zA-Z]+',miaoshu_xinghao))
    if pinpai_xinghao !='':
        seg_list = list(jieba.cut(pinpai_xinghao, cut_all=False))
        pinpai = seg_list[0]
        xinghao = ''
        if len(seg_list)>1:
            xinghao = seg_list[1]
        print(pinpai,xinghao)
    #处理操作
    #处理故障描述
    for sentence in miaoshu_xianxiang:
        #处理顿号“、”
        sentence_seged = jieba.posseg.cut(sentence.strip())
        zhuyu = []

        for x in sentence_seged:
            if (x.flag == 'n' or x.flag == 'x'):
                if x.word in buweizhuyu:
                    buwei_xianxiang_title.append(x.word)
                    xianxaing_buwei_title.append(sentence)
                    if x.word not in zhuyu_list:
                        zhuyu_list.append(x.word)
            if '报警' in sentence:
                if x.flag == 'eng' or x.flag == 'm':
                    if not (x.word >= u'\u4e00' and x.word <= u'\u9fa5'):#判断是否是汉字
                        if x.word not in baojing_list:
                            baojing_list.append(x.word)
                        baojing_xianxiang_title.append(x.word)
                        xianxaing_baojing_title.append(sentence)

        # cut_statement = thu_lac.cut(sentence,text=False)
        # print(cut_statement)
result0 = pd.DataFrame()
result0['title'] = yuanyindb
result0.to_csv('neo4j/yuanyin2.csv', index=None,encoding='utf-8')

result1 = pd.DataFrame()
result1['title1'] = caozuo_title
result1['relation'] = ['引起']*len(caozuo_title)
result1['title2'] = xianxiang_caozuo_title
result1.to_csv('neo4j/caozuoxianxaing.csv', index=None,encoding='utf-8')

result2 = pd.DataFrame()
result2['title1'] = xianxiang_yuanyin_title
result2['relation'] = ['间接原因']*len(xianxiang_yuanyin_title)
result2['title2'] = yuanyin_title
result2.to_csv('neo4j/xianxiangyuanyin.csv', index=None,encoding='utf-8')

result3 = pd.DataFrame()
result3['title1'] = xianxiang_title1
result3['relation'] = ['相关']*len(xianxiang_title1)
result3['title2'] = xianxiang_title2
result3.to_csv('neo4j/xianxiangxianxiang.csv', index=None,encoding='utf-8')

result3 = pd.DataFrame()
result3['title1'] = xianxaing_buwei_title
result3['relation'] = ['故障部位']*len(xianxaing_buwei_title)
result3['title2'] = buwei_xianxiang_title
result3.to_csv('neo4j/xianxaingbuwei.csv', index=None,encoding='utf-8')

result3 = pd.DataFrame()
result3['title1'] = xianxaing_baojing_title
result3['relation'] = ['报警信息']*len(xianxaing_baojing_title)
result3['title2'] = baojing_xianxiang_title
result3.to_csv('neo4j/xianxaingbaojing.csv', index=None,encoding='utf-8')

# result1 = pd.DataFrame()
# result1['title'] = zhuyu_list
# result1.to_csv('zhuyu.csv', index=None,encoding='utf-8')
# result = pd.DataFrame()
# result['title'] = caozuo_list
# result.to_csv('caozuo.csv', index=None,encoding='utf-8')
# result2 = pd.DataFrame()
# result2['title'] = xianxiang_list
# result2.to_csv('xianxiang.csv', index=None,encoding='utf-8')
# result3 = pd.DataFrame()
# result3['title'] = baojing_list
# result3.to_csv('baojing.csv', index=None,encoding='utf-8')
#
# f1 = open('caozuo.txt','w+',encoding='utf-8')
# f2 = open('xianxiang.txt','w+',encoding='utf-8')
# f3 = open('buwei.txt','w+',encoding='utf-8')
# f4 = open('baojing.txt','w+',encoding='utf-8')
# for zhuyu in zhuyu_list:
#     f3.write(zhuyu+'\n')
# f3.close()
# for caozuo in caozuo_list:
#     f1.write(caozuo+'\n')
# f1.close()
# for xianxiang in xianxiang_list:
#     f2.write(xianxiang+'\n')
# f2.close()
# for baojing in baojing_list:
#     f4.write(baojing+'\n')
# f4.close()
