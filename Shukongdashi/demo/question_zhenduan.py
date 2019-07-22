import json
import re
import pymysql
import jieba.posseg
import jieba
import os
from Shukongdashi.demo import cosin
from Shukongdashi.toolkit.pre_load import neo_con
from Shukongdashi.toolkit.pre_load import cnn_model
from django.http import HttpResponse
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


# 实现简单匹配selectedlist是解析出来用户输入的信息，selectedlist
def getTuili(pinpai, xinghao, errorid, describe, relationList, ret_dict):
    print( errorid, describe, relationList, ret_dict)
    if errorid!='':
        describe += '，' + errorid + '报警'
    print('目录：',os.path.dirname(os.getcwd()))
    jieba.load_userdict(os.getcwd()+'\\Shukongdashi\\demo\\fencidian.txt')
    pattern = r'\.|;|。|；|！'
    pattern2 = r',|，'

    # 加载停用词
    stopwords = []
    with open(os.getcwd()+'\\Shukongdashi\\demo\\stopwords.txt', 'r', encoding='utf-8') as f:
        st = f.readlines()
    for line in st:
        line = line.strip().encode('utf-8').decode('utf-8-sig')
        stopwords.append(line)
    # 加载故障部位
    buweizhuyu = []
    with open(os.getcwd()+'\\Shukongdashi\\demo\\zhuyu.txt', 'r', encoding='utf-8') as f:
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
    miaoshu_xinghao = []
    miaoshu_caozuo = []
    miaoshu_xianxiang = []
    for jvzi in miaoshu_jvzi:
        # 把句子进一步拆分
        miaoshu_list = re.split(pattern2, jvzi)
        miaoshu_list = list(filter(None, miaoshu_list))
        # 判断类型,把相同的类型放到一起
        for miaoshu in miaoshu_list:
            miaoshu_type = cnnModel.predict(miaoshu)
            if miaoshu_type == '机床类型':
                miaoshu_xinghao.append(miaoshu)
            elif miaoshu_type == '执行操作':
                miaoshu_caozuo.append(miaoshu)
            elif miaoshu_type == '故障现象':
                miaoshu_xianxiang.append(miaoshu)
    # 到此，不同的描述放到了不同的list里
    print(miaoshu_caozuo, miaoshu_xianxiang)
    # 处理品牌型号描述
    miaoshu_xinghao = ''.join(miaoshu_xinghao)
    pinpai_xinghao = ''.join(re.findall(u'[0-9a-zA-Z]+', miaoshu_xinghao))
    if pinpai_xinghao != '':
        seg_list = list(jieba.cut(pinpai_xinghao, cut_all=False))
        pinpai = seg_list[0]
        xinghao = ''
        if len(seg_list) > 1:
            xinghao = seg_list[1]
        print(pinpai, xinghao)
    # 处理操作

    # 处理故障描述,寻找部位和故障代码
    buweilist = []
    erroridlist = []
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
    # print(buweilist, erroridlist)
    # 根据执行了的操作推理导致的现象
    # 相关的操作
    similarcaozuos = []
    for caozuo in miaoshu_xianxiang:
        for caozuodb in findEntitiesByType('Caozuo'):
            similar = cosin.sentence_resemble(caozuo, caozuodb)
            if similar > 0.8:
                similarcaozuos.append(caozuodb)
    # print('similarcaozuos:', similarcaozuos)
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
    # print('relationguzhangs:', relationguzhangs)
    # 寻找相似现象
    similarxianxiang = miaoshu_xianxiang
    for i,xianxiang in enumerate(miaoshu_xianxiang):
        for relationguzhang in relationguzhangs:
            similar = cosin.sentence_resemble(xianxiang, relationguzhang)
            if similar > 0.8:
                similarxianxiang[i] = relationguzhang
    print('similarxianxiang:', similarxianxiang)
    # 找出所有相似现象
    if len(buweilist) == 0 or len(erroridlist) == 0:
        for i,xianxiang in enumerate(similarxianxiang):
            for xianxiangdb in findEntitiesByType('Xianxiang'):
                similar = cosin.sentence_resemble(xianxiang, xianxiangdb)
                if similar > 0.8:
                    similarxianxiang[i] = xianxiangdb
        print('similar:',similarxianxiang)
        print('relationList:', relationList)
    similarxianxiang += relationList

    # print('similarxianxiang:',similarxianxiang)
    temp = {}
    temp = temp.fromkeys(similarxianxiang)
    selectedlist = list(temp.keys())
    # 推理原因，推理相关现象
    tuilixianxiang = []
    for xianxiang in selectedlist:
        tuilixianxiang += findEntities(xianxiang, '相关')
    # 删除重复
    tuilixianxiangtemp = []
    for chongfu in tuilixianxiang:
        if (chongfu not in selectedlist) and (chongfu not in tuilixianxiangtemp):
            tuilixianxiangtemp.append(chongfu)
    tuilixianxiang = tuilixianxiangtemp
    # 根据这个error_list查找一个和里面元素相关的元素，作数组返回
    ret_dict['selectedlist'] = selectedlist
    ret_dict['hiddenlist'] = tuilixianxiang
    count = {}
    # 根据现象查找可能的原因，将可能的原因作为键，将契合的次数作为值
    for xianxiang in selectedlist:
        jainjieyuanyindb = db.findOtherEntities(xianxiang, "间接原因")
        selected_index = [i for i in range(len(jainjieyuanyindb))]
        for i in selected_index:
            jianjieyuanyin = jainjieyuanyindb[i]['n2']['title']
            count.setdefault(jianjieyuanyin, 0)
            count[jianjieyuanyin] = count[jianjieyuanyin] + 1
    # 根据可能性重新对最终原因进行排序
    for i, j in count.items():
        # print(str(i) + ":", j)
        relathionCount = db.findNumberOfEntities1(i, "间接原因")[0]["relathionCount"]
        count[i] = round(j / relathionCount, 2)
    # 对相关原因按匹配次数排序
    list1 = sorted(count.items(), key=lambda x: x[1], reverse=True)
    for yuanyinItem in list1:
        # 查解决方法
        jiejuelist = []
        db_mysql = pymysql.connect(host='localhost', user='root', password='root', db='sg_faq')
        cursor = db_mysql.cursor()  # 获取指针以操作数据库
        cursor.execute('set names utf8')
        print(yuanyinItem)
        sql = "select guzhangfenxi FROM guzhanganli where guzhangyuanyin = '%s'" % (yuanyinItem[0])
        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            for row in results:
                jiejuelist.append(row[0])
        except:
            print("Error: unable to fetch data")
        # 关闭数据库连接
        db_mysql.close()
        # 查找间接导致原因的现象个数#计算可能性
        xianxiangdb = db.findOtherEntities2(yuanyinItem[0], "间接原因")
        relathionCount = len(xianxiangdb)
        selected_index2 = [i for i in range(len(xianxiangdb))]
        tuililist = []
        for i in selected_index2:
            xianxiang = xianxiangdb[i]['n1']['title']
            if xianxiang in selectedlist:
                zhijieyuanyindb = db.findOtherEntities(xianxiang, "直接原因")
                if len(zhijieyuanyindb) > 0:
                    zhijieyuanyi = zhijieyuanyindb[0]['n2']['title']
                    tuililist.append(
                        {"entity1": xianxiang, "rel": "含义", "entity2": zhijieyuanyi, "entity1_type": "故障代码",
                         "entity2_type": "含义"})
                    tuililist.append(
                        {"entity1": zhijieyuanyi, "rel": "间接原因", "entity2": yuanyinItem[0], "entity1_type": "含义",
                         "entity2_type": "最终原因"})
                else:
                    tuililist.append(
                        {"entity1": xianxiang, "rel": "间接原因", "entity2": yuanyinItem[0], "entity1_type": "现象",
                         "entity2_type": "最终原因"})
        for jiejue in jiejuelist:
            tuililist.append({"entity1": yuanyinItem[0], "rel": "解决办法", "entity2": jiejue, "entity1_type": "最终原因",
                              "entity2_type": "解决办法"})
        if (ret_dict.get('list') is None):
            ret_dict['list'] = []
        ret_dict['list'].append(
            {"yuanyin": yuanyinItem[0], "answer": jiejuelist, "possibility": yuanyinItem[1], "list": tuililist})
        print(ret_dict)
    return ret_dict


def findHiddenList(selectedlist):
    hiddenlist = []
    for i in selectedlist:
        hidden_db = db.findOtherEntities(i, "相关")
        hidden_index = [i for i in range(len(hidden_db))]
        for i in hidden_index:
            hidden_title = hidden_db[i]['n2']['title']
            if hidden_title not in hiddenlist and hidden_title not in selectedlist:
                hiddenlist.append(hidden_title)
    return hiddenlist



def question_tuili():
    relationListtmp = 'CNC显示ALM411|'
    relationList = relationListtmp.split('|')
    for i in range(len(relationList)):
        if relationList[i] == '':
            del (relationList[i])
    ret_dict = {}
    pinpai = '发那科'
    xinghao = 'GSK928TA'
    errorid = 'ALM413'
    question = '开机时，坐标轴快速运动，电压模块报警，系统无法工作'  # '某配套FANUC OMC的数控铣床，在加工过程中突然断电，重新开机，系 统电源无法正常接通。'
    ret_dict = getTuili(pinpai, xinghao, errorid, question, relationList, ret_dict)
    if (len(ret_dict) != 0):
        return json.dumps(ret_dict, ensure_ascii=False)
    return json.dumps('没有找到类似的答案', ensure_ascii=False)

if __name__ == '__main__':
    print(question_tuili())

def question_answering(request):  # index页面需要一开始就加载的内容写在这里
    if (request.GET):
        ret_dict = {}
        pinpai = ''
        xinghao = ''
        errorid = ''
        question = ''
        relationListtmp = ''
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
            relationListtmp = request.GET['relationList']
        except:
            pass

        relationList = relationListtmp.split('|')
        for i in range(len(relationList)):
            if relationList[i] == '':
                del (relationList[i])
        if (errorid is not None or question is not None):
            ret_dict = getTuili(pinpai, xinghao, errorid, question, relationList, ret_dict)
        if (ret_dict.get('list') is not None):
            return HttpResponse(json.dumps(ret_dict, ensure_ascii=False), content_type="application/json;charset=utf-8")
        else:
            return HttpResponse(json.dumps('没有找到类似的答案', ensure_ascii=False), content_type="application/json;charset=utf-8")
    else:
        return HttpResponse(json.dumps("没有参数的请求", ensure_ascii=False))
