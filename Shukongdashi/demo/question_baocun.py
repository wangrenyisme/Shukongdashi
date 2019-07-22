import os
import json
import re
from Shukongdashi.toolkit.pre_load import cnn_model
import jieba
import jieba.posseg
from django.http import HttpResponse
from itertools import combinations
from Shukongdashi.demo import cosin
from Shukongdashi.toolkit.pre_load import neo_con
import random
import pymysql

db_mysql = pymysql.connect(host='localhost', user='root', password='root', db='sg_faq')
cursor = db_mysql.cursor()  # 获取指针以操作数据库
cursor.execute('set names utf8')
db = neo_con
cnnModel = cnn_model


# 查找所有属于某类型的实体
def findEntitiesByType(type):
    entitydb = db.findEntitiesByType(type)
    selected_index = [i for i in range(len(entitydb))]
    entitylist = []
    for i in selected_index:
        entitylist.append(entitydb[i]['m']['title'])
    return entitylist


# 查找实体,关系,返回第一个实体列表
def findEntities2(entity2, relation):
    entitydb = db.findOtherEntities2(entity2, relation)
    selected_index = [i for i in range(len(entitydb))]
    entitylist = []
    for i in selected_index:
        entitylist.append(entitydb[i]['n1']['title'])
    return entitylist


# 查找实体,关系,返回第二个实体列表
def findEntities(entity1, relation):
    entitydb = db.findOtherEntities(entity1, relation)
    selected_index = [i for i in range(len(entitydb))]
    entitylist = []
    for i in selected_index:
        entitylist.append(entitydb[i]['n2']['title'])
    return entitylist


# 查找是否包含实体
def findEntitys(entity1, relation, entity2):
    yuanyin = db.findOtherEntities(entity1, relation)
    selected_index = [i for i in range(len(yuanyin))]
    list = []
    for i in selected_index:
        list.append(yuanyin[i]['n2']['title'])
    if entity2 in list:
        return True
    return False


# 查找相似的描述,返回描述
def findLikeEntitys(entity1, relation, entity2):
    yuanyin = db.findOtherEntities(entity1, relation)
    selected_index = [i for i in range(len(yuanyin))]
    list = []
    for i in selected_index:
        list.append(yuanyin[i]['n2']['title'])
    if len(list) != 0:
        describes = findSimilarEntitys(entity2, list)
        return describes
    return str(0)


def findSimilarEntitys(entity, list):
    dictionary = {}  # 用于计算相似度后，把解决方案、对应id、相似度存入字典，根据相似度大小逆序输出
    for desc in list:
        similar = cosin.sentence_resemble(entity, desc)
        if similar > 0.55:
            dictionary.update({desc: str(round(similar * 100, 2)) + '%'})  # 将id，描述，解决方法，以及对应的相似度加入字典
    dictionary = sorted(dictionary.items(), key=lambda item: item[1], reverse=True)  # 对字典根据相似度进行降序排序
    # 暂且全部输出
    return dictionary


# 插入描述和答案
def insertDescAndAnsw(describe, answer):
    try:
        if (len(db.findNode(describe)) == 0):
            db.insertNode(describe, 'Describe')
        if (len(db.findNode(answer)) == 0):
            db.insertNode(answer, 'Answer')
        db.insertRelation(describe, '解决方法', answer, 'Describe', 'Answer')
    except:
        print('插入失败')
        return False
    return True


def insertTwoNodes(entity1, relation, entity2, lable1, lable2):
    try:
        if (len(db.findNode(entity1)) == 0):
            print('len(db.findNode(entity1)) == 0')
            db.insertNode(entity1, lable1)
        if (len(db.findNode(entity2)) == 0):
            db.insertNode(entity2, lable2)
        db.insertRelation(entity1, relation, entity2, lable1, lable2)
    except:
        print('插入失败')
        return False
    return True


def insertPa(pinpai, xinghao, errorid, describe, selectedList, yuanyin, answer):
    jieba.load_userdict(os.getcwd() + '\\Shukongdashi\\demo\\fencidian.txt')
    pattern = r'\.|;|。|；|！'
    pattern2 = r',|，'

    # 加载停用词
    stopwords = []
    with open(os.getcwd() + '\\Shukongdashi\\demo\\stopwords.txt', 'r', encoding='utf-8') as f:
        st = f.readlines()
    for line in st:
        line = line.strip().encode('utf-8').decode('utf-8-sig')
        stopwords.append(line)
    # 加载故障部位
    buweizhuyu = []
    with open(os.getcwd() + '\\Shukongdashi\\demo\\zhuyu.txt', 'r', encoding='utf-8') as f:
        st = f.readlines()
    for line in st:
        line = line.strip().encode('utf-8').decode('utf-8-sig')  # 防止BOM现象
        buweizhuyu.append(line)

    miaoshu = describe.replace(' ', '')
    print(u'正在过滤停用词......')
    miaoshu_baocun = []
    miaoshu_cut = jieba.cut(miaoshu)
    for m in miaoshu_cut:
        if m not in stopwords:
            miaoshu_baocun.append(m)
    miaoshu = ''.join(miaoshu_baocun)

    miaoshu_jvzi = re.split(pattern, miaoshu)
    miaoshu_jvzi = list(filter(None, miaoshu_jvzi))
    # 保存描述中描述品牌型号、执行操作、报警现象的内容
    miaoshu_caozuo = []
    miaoshu_xianxiang = []
    for jvzi in miaoshu_jvzi:
        # 把句子进一步拆分
        miaoshu_list = re.split(pattern2, jvzi)
        miaoshu_list = list(filter(None, miaoshu_list))
        # 判断类型,把相同的类型放到一起
        for miaoshu in miaoshu_list:
            miaoshu_type = cnnModel.predict(miaoshu)
            if miaoshu_type == '执行操作':
                miaoshu_caozuo.append(miaoshu)
            elif miaoshu_type == '故障现象':
                miaoshu_xianxiang.append(miaoshu)
    # 到此，不同的描述放到了不同的list里
    print('执行操作:', miaoshu_caozuo)
    print('故障现象:', miaoshu_xianxiang)
    yuanyin_this = ''
    try:
        yuanyin_this = miaoshu_xianxiang[len(miaoshu_xianxiang) - 1] + '的故障'
    except:
        yuanyin_this = '未知原因引起的故障'
    print(yuanyin_this)
    erroridlist = re.split(',|，', errorid)
    buweilist = []
    for sentence in miaoshu_xianxiang:
        # 处理顿号“、”
        sentence_seged = jieba.posseg.cut(sentence.strip())
        for x in sentence_seged:
            if (x.flag == 'n' or x.flag == 'x'):
                if x.word in buweizhuyu:
                    buweilist.append(x.word)
            if '报警' in sentence:
                if x.flag == 'eng' or x.flag == 'm':
                    if not (x.word >= u'\u4e00' and x.word <= u'\u9fa5'):  # 判断是否是汉字
                        erroridlist.append(x.word)
    print(buweilist, erroridlist)
    # 相关的操作
    similarcaozuos = miaoshu_caozuo
    for i, caozuo in enumerate(miaoshu_caozuo):
        for caozuodb in findEntitiesByType('Caozuo'):
            similar = cosin.sentence_resemble(caozuo, caozuodb)
            if similar > 0.8:
                similarcaozuos[i] = caozuodb
    # 相关故障
    relationguzhangs = []
    # 相关操作引起的现象
    for caozuo in similarcaozuos:
        relationguzhangs += findEntities(caozuo, '引起')

    # 根据故障部位和报警信息寻找现象

    for entity2 in buweilist:
        relationguzhangs += findEntities2(entity2, '故障部位')
    for entity2 in erroridlist:
        relationguzhangs += findEntities2(entity2, '报警信息')
    print('relationguzhangs:', relationguzhangs)

    similarxianxiang = miaoshu_xianxiang  # selectedList
    for i,xianxiang in enumerate(miaoshu_xianxiang):
        for relationguzhang in relationguzhangs:
            similar = cosin.sentence_resemble(xianxiang, relationguzhang)
            if similar > 0.8:
                similarxianxiang[i] = relationguzhang
    print('similarxianxiang:', similarxianxiang)
    # similarcaozuos,similarxianxiang,erroridlist,
    # yuanyin,jiejuebanfa

    # 初始化操作和故障，故障和原因之间的关系
    for xianxiang in similarxianxiang:
        for caozuo in similarcaozuos:
            insertTwoNodes(caozuo, '引起', xianxiang, 'Caozuo', 'Xianxiang')
        insertTwoNodes(xianxiang, '间接原因', yuanyin_this, 'Xianxiang', 'Yuanyin')
    # 故障现象之间的关联关系
    zuhe_xianxiaing = list(combinations(similarxianxiang, 2))
    for zuhe in zuhe_xianxiaing:
        insertTwoNodes(zuhe[0], '相关', zuhe[1], 'Xianxiang', 'Xianxiang')
        insertTwoNodes(zuhe[1], '相关', zuhe[0], 'Xianxiang', 'Xianxiang')

    for sentence in similarxianxiang:
        # 处理顿号“、”
        sentence_seged = jieba.posseg.cut(sentence.strip())
        zhuyu = []

        for x in sentence_seged:
            if (x.flag == 'n' or x.flag == 'x'):
                if x.word in buweizhuyu:
                    insertTwoNodes(sentence, '故障部位', x.word, 'Xianxiang', 'GuzhangBuwei')
            if '报警' in sentence:
                if x.flag == 'eng' or x.flag == 'm':
                    if not (x.word >= u'\u4e00' and x.word <= u'\u9fa5'):  # 判断是否是汉字
                        insertTwoNodes(sentence, '报警信息', x.word, 'Xianxiang', 'Errorid')
    # 报警信息和所有现象关联
    # 最好判断一下是否已经存在关系了

    answer = answer.replace("'", "\\\'").replace('"', '\\\"')
    t = (yuanyin_this, describe + ",".join(selectedList), answer)
    sql = "insert into guzhanganli values('%s','%s','%s')" % t
    print(sql)
    # try:
    # 执行SQL语句
    cursor.execute(sql)
    # 获取所有记录列表
    db_mysql.commit()  # 提交，不然无法保存插入或者修改的数据(这个一定不要忘记加上)
    #cursor.close()
    # 关闭数据库连接
    #db_mysql.close()  # 关闭连接
    return True
    # except:
    #     print("Error: insert error!")
    #     return False


def question_baocun(request):  # index页面需要一开始就加载的内容写在这里
    message = '没有参数的提交'
    if (request.GET):
        pinpai = ''
        xinghao = ''
        errorid = ''
        question = ''
        yuanyin = ''
        answer = ''
        selectedListtmp = ''
        try:
            pinpai = request.GET['pinpai']
        except:
            pass
        try:
            xinghao = request.GET['xinghao']
        except:
            pass
        try:
            errorid = request.GET['errorid']
        except:
            pass
        try:
            question = request.GET['question']
        except:
            pass
        try:
            selectedListtmp = request.GET['selectedList']
        except:
            pass
        try:
            yuanyin = request.GET['yuanyin']
        except:
            pass
        try:
            answer = request.GET['answer']
        except:
            pass

        selectedList = selectedListtmp.split('|')
        for i in range(len(selectedList)):
            if selectedList[i] == '':
                del (selectedList[i])
        if (pinpai is not None or xinghao is not None or errorid is not None or question is not None):
            if (insertPa(pinpai, xinghao, errorid, question, selectedList, yuanyin, answer)):
                message = '保存成功'
            else:
                message = '保存失败'
        else:
            message = '没有参数的提交'
    ret_dict = {'message': message}
    return HttpResponse(json.dumps(ret_dict, ensure_ascii=False), content_type="application/json;charset=utf-8")
