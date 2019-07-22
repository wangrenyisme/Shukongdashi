import os
import json
from django.http import HttpResponse
import difflib
from Shukongdashi.toolkit.pre_load import neo_con
import random

db = neo_con


# 对描述进行模糊查询,返回描述s
def findLikeEntitys(question_start):
    items = db.findBuquanItems(question_start)
    selected_index = [i for i in range(len(items))]
    list = []
    for i in selected_index:
        list.append(items[i]['n']['title'])
    return list


# #实现简单匹配selectedlist是解析出来用户输入的信息，selectedlist
def getBuquanQuestions(question_start, ret_dict):
    items = db.findBuquanItems(question_start)
    selected_index = [i for i in range(len(items))]
    list = []
    i = 0
    for i in selected_index:
        list.append(items[i]['n']['title'])
        i = i + 1
        if i == 5:
            break
    ret_dict['list'] = list
    return ret_dict


def question_buquan(request):  # index页面需要一开始就加载的内容写在这里
    if (request.GET):
        ret_dict = {}
        question_start = ''
        try:
            question_start = request.GET['question_start']
        except:
            pass
        if (question_start is not None and question_start != ''):
            ret_dict = getBuquanQuestions(question_start, ret_dict)
        if (len(ret_dict) != 0 and ret_dict != 0):
            return HttpResponse(json.dumps(ret_dict, ensure_ascii=False), content_type="application/json;charset=utf-8")
        return HttpResponse(json.dumps('没有找到类似的答案', ensure_ascii=False), content_type="application/json;charset=utf-8")
    else:
        return HttpResponse(json.dumps("没有参数的请求", ensure_ascii=False))
