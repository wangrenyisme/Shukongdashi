import os
import json
import re
from decimal import *

import jieba
from django.http import HttpResponse
import difflib

from Shukongdashi.demo import cosin
from Shukongdashi.toolkit.pre_load import neo_con
import random

db = neo_con


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


def insertPa(pinpai, xinghao, errorid, describe, answer,ret_dict):
    if (insertTwoNodes(describe, '解决方法', answer, 'Describe', 'Answer')):  # 完成了描述和解决的插入
        if (len(errorid) > 0):  # 故障代码的故障描述
            if (insertTwoNodes(errorid, '故障描述', describe, 'Errorid', 'Describe')):
                if (len(xinghao) > 0):  # 有型号就有故障代码
                    if (insertTwoNodes(xinghao, '故障代码', errorid, 'Xinghao', 'Errorid')):
                        insertTwoNodes(pinpai, '型号', xinghao, 'Pinpai', 'Xinghao')
                elif (len(pinpai) > 0):
                    insertTwoNodes(pinpai, '故障描述', describe, 'Pinpai', 'Describe')
        elif (len(xinghao) > 0):  # 型号的故障描述
            if (insertTwoNodes(xinghao, '故障描述', describe, 'Xinghao', 'Describe')):
                insertTwoNodes(pinpai, '型号', xinghao, 'Pinpai', 'Xinghao')
        elif (len(pinpai) > 0):  # 品牌的故障描述
            insertTwoNodes(pinpai, '故障描述', describe, 'Pinpai', 'Describe')
        return True
    else:
        return False


def question_baocun(request):  # index页面需要一开始就加载的内容写在这里
    message = '没有参数的提交'
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
        if (pinpai is not None or xinghao is not None or errorid is not None or question is not None):
            if (insertPa(pinpai, xinghao, errorid, question, relationList, ret_dict)):
                message = '保存成功'
            else:
                message = '保存失败'
        else:
            message = '没有参数的提交'
    ret_dict = {'message': message}
    return HttpResponse(json.dumps(ret_dict, ensure_ascii=False), content_type="application/json;charset=utf-8")
