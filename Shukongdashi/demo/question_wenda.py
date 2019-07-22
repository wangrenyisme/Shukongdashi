import re
from Shukongdashi.toolkit.pre_load import neo_con
from Shukongdashi.demo import cosin
from django.http import HttpResponse
import json
db = neo_con
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


def huida(q_type, zhuyu):
    print(zhuyu,':')
    daanlist = []
    # 某故障原因 会引起哪些现象
    if q_type == 0:
        relationyuanyins = []
        for yuanyindb in findEntitiesByType('Yuanyin'):
            similar = cosin.sentence_resemble(zhuyu, yuanyindb)
            if similar > 0.8:
                relationyuanyins.append(yuanyindb)
        print('relationyuanyins:', relationyuanyins)
        for relationyuanyin in relationyuanyins:
            daanlist += findEntities2(relationyuanyin, '间接原因')
        templist = []
        for temp in daanlist:
            if temp.isalnum():
                templist.append(temp+'报警')
        daanlist = templist
    # 做什么操作 会遇到什么错误
    if q_type == 1:
        relationcaozuos = []
        for caozuodb in findEntitiesByType('Caozuo'):
            similar = cosin.sentence_resemble(zhuyu, caozuodb)
            if similar > 0.8:
                relationcaozuos.append(caozuodb)
        print('relationcaozuos:', relationcaozuos)
        for caozuo in relationcaozuos:
            daanlist += findEntities(caozuo, '引起')

    # 某部位 常出现哪些故障
    if q_type == 2:
        daanlist = findEntities2(zhuyu, '故障部位')
    # 报警的含义是什么
    if q_type == 3:
        daanlist = findEntities(zhuyu, '直接原因')
    temp = {}
    temp = temp.fromkeys(daanlist)
    daanlist = list(temp.keys())
    return daanlist
pattern = [[r"会引起哪些现象",r"会引起什么现象",r"引起的现象",r"会引起的现象",r"引起的现象有哪些"],
           [r"会遇到什么错误",r"会遇到的错误",r"会遇到哪些错误"],
           [r"部位常出现哪些故障",r"部位常遇到的故障",r"部位常见的故障"],
           [r"报警的含义是什么",r"报警的含义",r"报警的原因",r"报警的原因是什么"]]

questions = ['外部24V短路的故障会引起哪些现象？',
             '手动移动X轴时会遇到什么错误？',
             '速度控制单元常出现哪些故障？',
             'ALM401报警的含义是什么？']
def question_wenda(request):
    ret_dict = {}
    ret_dict['answer'] = []
    if (request.GET):

        question = ''
        try:
            question = request.GET['question']
        except:
            pass
        if question !='':
            pos = -1
            q_type = -1
            for i in range(len(pattern)):
                for x in pattern[i]:
                    index = re.search(x, question)
                    if (index):
                        pos = index.span()[0]
                        q_type = i
                        break
                if (pos != -1):
                    break
            zhuyu = question[0:pos]
            print('zhuyu:',zhuyu)
            ret_dict['answer'] += huida(q_type, zhuyu)
    return HttpResponse(json.dumps(ret_dict, ensure_ascii=False), content_type="application/json;charset=utf-8")