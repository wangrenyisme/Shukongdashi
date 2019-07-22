import os
import json
from django.http import HttpResponse
import difflib
from Shukongdashi.toolkit.pre_load import neo_con
import random

question_list = []

with open(os.path.dirname(os.getcwd())+'/label_data/questions.txt','r',encoding='utf8') as fr:
	for question in fr.readlines():
		question_list.append(question.strip())
db = neo_con
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
# #实现简单匹配selectedlist是解析出来用户输入的信息，selectedlist
def getSelectAndHidden(pinpai,xinghao,errorid,describe, ret_dict):
	selectedlist = []
	if pinpai == "发那科":
		if len(errorid)>0:
			selectedlist = errorid.split(',')
			if len(selectedlist)==1:
				selectedlist = errorid.split('，')
		if len(describe)>0:
			selectedlist.append(describe)
		#根据这个error_list查找一个和里面元素相关的元素，作数组返回
		ret_dict['selectedlist'] = selectedlist
		ret_dict['hiddenlist'] = findHiddenList(selectedlist)
	return ret_dict
def question_fenxi():  # index页面需要一开始就加载的内容写在这里
	ret_dict = {}
	pinpai = '发那科'
	xinghao = 'GSK928TA'
	errorid = 'ALM401'
	question = '搬迁后,首次开机时,机床出现剧烈振动'
	if (pinpai is not None or xinghao is not None or errorid is not None or question is not None):
		ret_dict = getSelectAndHidden(pinpai, xinghao, errorid, question, ret_dict)
	if (len(ret_dict) != 0):
		return json.dumps(ret_dict, ensure_ascii=False)
	return json.dumps('没有找到类似的答案', ensure_ascii=False)
if __name__ == '__main__':
	print(question_fenxi())