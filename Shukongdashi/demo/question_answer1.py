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
def findEntitys(entity1,relation,entity2):
	yuanyin = db.findOtherEntities(entity1, relation)
	selected_index = [i for i in range(len(yuanyin))]
	list = []
	for i in selected_index:
		list.append(yuanyin[i]['n2']['title'])
	if entity2 in list:
		return True
	return False
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
#实现简单匹配selectedlist是解析出来用户输入的信息，selectedlist
def getTuili(pinpai,xinghao,errorid,describe,relationList,ret_dict):
	selectedlist = []
	if pinpai == "发那科":
		if len(errorid) > 0:
			selectedlist = errorid.split(',')
			if len(selectedlist) == 1:
				selectedlist = errorid.split('，')
		if len(describe) > 0:
			selectedlist.append(describe)
		# 根据这个error_list查找一个和里面元素相关的元素，作数组返回
		ret_dict['selectedlist'] = selectedlist
		ret_dict['hiddenlist'] = findHiddenList(selectedlist)
	relationList = relationList +selectedlist
	count = {}
	#根据现象查找可能的原因，将可能的原因作为键，将契合的次数作为值
	for item in relationList:
		jainjieyuanyindb = db.findOtherEntities(item, "间接原因")
		selected_index = [i for i in range(len(jainjieyuanyindb))]
		for i in selected_index:
			jianjieyuanyin = jainjieyuanyindb[i]['n2']['title']
			count.setdefault(jianjieyuanyin, 0)
			count[jianjieyuanyin] = count[jianjieyuanyin] + 1
	#根据可能性重新对最终原因进行排序
	for i, j in count.items():
		#print(str(i) + ":", j)
		relathionCount = db.findNumberOfEntities1(i, "间接原因")[0]["relathionCount"]
		count[i] = round(j/relathionCount,2)
	#对相关原因按匹配次数排序
	list1 = sorted(count.items(), key=lambda x: x[1],reverse=True)
	for yuanyinItem in list1:
		#查解决方法
		jiejuedb = db.findOtherEntities(yuanyinItem[0], "解决方法")
		selected_index = [i for i in range(len(jiejuedb))]
		jiejuelist = []
		for i in selected_index:
			jiejue = jiejuedb[i]['n2']['title']
			jiejuelist.append(jiejue)

		#查找间接导致原因的现象个数#计算可能性
		xianxiangdb = db.findOtherEntities2(yuanyinItem[0], "间接原因")
		relathionCount = len(xianxiangdb)
		selected_index2 = [i for i in range(len(xianxiangdb))]
		list = []
		for i in selected_index2:
			xianxiang = xianxiangdb[i]['n1']['title']
			if xianxiang in relationList:
				zhijieyuanyindb = db.findOtherEntities(xianxiang, "直接原因")
				if len(zhijieyuanyindb)>0:
					zhijieyuanyi = zhijieyuanyindb[0]['n2']['title']
					list.append({"entity1": xianxiang, "rel": "含义", "entity2": zhijieyuanyi, "entity1_type": "故障代码",
								 "entity2_type": "含义"})
					list.append({"entity1": zhijieyuanyi, "rel": "间接原因", "entity2": yuanyinItem[0], "entity1_type": "含义",
								 "entity2_type": "最终原因"})
				else:
					list.append({"entity1": xianxiang, "rel": "间接原因", "entity2": yuanyinItem[0], "entity1_type": "现象",
				 "entity2_type": "最终原因"})
		for jiejue in jiejuelist:
			list.append({"entity1": yuanyinItem[0], "rel": "解决办法", "entity2": jiejue, "entity1_type": "最终原因",
						 "entity2_type": "解决办法"})
		if (ret_dict.get('list') is None):
			ret_dict['list'] = []
		ret_dict['list'].append(
			{"yuanyin": yuanyinItem[0], "answer": jiejuelist, "possibility": yuanyinItem[1],"list":list})

	return ret_dict

def get_yuanyin(question, ret_dict):
	yuanyin = db.findOtherEntities(question, "或因为")
	selected_index = [i for i in range(len(yuanyin))]
	for i in selected_index:
		selected_plant = yuanyin[i]['n2']['title']
		if (ret_dict.get('list') is None):
			ret_dict['list'] = []
		ret_dict['list'].append(
			{"entity1": question, "rel": "或因为", "entity2": selected_plant, "entity1_type": "xianxiang", "entity2_type": "yuanyin"})
		if (ret_dict.get('answer') is None):
			ret_dict['answer'] = [selected_plant]
		else:
			ret_dict['answer'].append(selected_plant)
	return ret_dict
#查找是否包含实体
def findEntitys(entity1,relation,entity2):
	yuanyin = db.findOtherEntities(entity1, relation)
	selected_index = [i for i in range(len(yuanyin))]
	list = []
	for i in selected_index:
		list.append(yuanyin[i]['n2']['title'])
	if entity2 in list:
		return True
	return False

#查找相似的描述,返回描述
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
def findSimilarEntitys(entity,list):
	dictionary = {}  # 用于计算相似度后，把解决方案、对应id、相似度存入字典，根据相似度大小逆序输出
	for desc in list:
		similar = cosin.sentence_resemble(entity, desc)
		if similar >0.6:
			dictionary.update({desc: str(round(similar*100,2))+'%'})  # 将id，描述，解决方法，以及对应的相似度加入字典
	dictionary = sorted(dictionary.items(), key=lambda item: item[1], reverse=True)  # 对字典根据相似度进行降序排序
	#暂且全部输出
	return dictionary
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
def get_answer(pinpai,xinghao,errorid,describe, ret_dict):
	#假设都有
	pinpai_xinghao = findEntitys(pinpai,'型号',xinghao)
	if pinpai_xinghao:
		if (ret_dict.get('list') is None):
			ret_dict['list'] = []
		ret_dict['list'].append(
			{"entity1": pinpai, "rel": "型号", "entity2": xinghao, "entity1_type": "品牌",
			 "entity2_type": "型号"})
		xinghao_errorid = findEntitys(xinghao,'故障代码',errorid)
		if xinghao_errorid:
			if (ret_dict.get('list') is None):
				ret_dict['list'] = []
			ret_dict['list'].append(
				{"entity1": xinghao, "rel": "故障代码", "entity2": errorid, "entity1_type": "型号",
				 "entity2_type": "故障代码"})
			errorid_describe = findLikeEntitys(errorid, '故障描述', describe)
			if len(errorid_describe) != 0 and errorid_describe != 0:
				for desc in errorid_describe:
					if (ret_dict.get('list') is None):
						ret_dict['list'] = []
					ret_dict['list'].append(
						{"entity1": errorid, "rel": "故障描述", "entity2": desc[0], "entity1_type": "故障代码",
						 "entity2_type": "故障描述"})
					guzhang_types = db.findOtherEntities(desc[0], "故障类型")
					selected_index = [i for i in range(len(guzhang_types))]
					for i in selected_index:
						guzhang_type = guzhang_types[i]['n2']['title']
						if (ret_dict.get('list') is None):
							ret_dict['list'] = []
						ret_dict['list'].append(
							{"entity1": desc[0], "rel": "故障类型", "entity2": guzhang_type, "entity1_type": "故障描述",
							 "entity2_type": "故障类型"})
					answers = db.findOtherEntities(desc[0], "解决方法")
					selected_index = [i for i in range(len(answers))]
					for i in selected_index:
						answer = answers[i]['n2']['title']
						if (ret_dict.get('list') is None):
							ret_dict['list'] = []
						ret_dict['list'].append(
							{"entity1": desc[0], "rel": "解决方法", "entity2": answer, "entity1_type": "故障描述",
							 "entity2_type": "解决方法"})
						if (ret_dict.get('describe') is None):
							ret_dict['describe'] = [desc[0]]
						else:
							ret_dict['describe'].append(desc[0])

						if (ret_dict.get('answer') is None):
							ret_dict['answer'] = [answer]
						else:
							ret_dict['answer'].append(answer)

						if (ret_dict.get('similar') is None):
							ret_dict['similar'] = [desc[1]]
						else:
							ret_dict['similar'].append(desc[1])
			else:
				print('查型号对应的故障')
				xinghao_describe = findLikeEntitys(xinghao, '故障描述', describe)
				if len(xinghao_describe) != 0 and xinghao_describe != 0:
					for desc in xinghao_describe:
						answers = db.findOtherEntities(desc[0], "解决方法")
						selected_index = [i for i in range(len(answers))]
						for i in selected_index:
							answer = answers[i]['n2']['title']
							if (ret_dict.get('list') is None):
								ret_dict['list'] = []
							ret_dict['list'].append(
								{"entity1": desc[0], "rel": "解决方法", "entity2": answer, "entity1_type": "故障描述",
								 "entity2_type": "解决方法"})

							if (ret_dict.get('describe') is None):
								ret_dict['describe'] = [desc[0]]
							else:
								ret_dict['describe'].append(desc[0])

							if (ret_dict.get('answer') is None):
								ret_dict['answer'] = [answer]
							else:
								ret_dict['answer'].append(answer)
							if (ret_dict.get('similar') is None):
								ret_dict['similar'] = [desc[1]]
							else:
								ret_dict['similar'].append(desc[1])
				else:#品牌对应的故障描述
					pinpai_describe = findLikeEntitys(pinpai, '故障描述', describe)
					if len(pinpai_describe) != 0 and pinpai_describe != 0:
						for desc in pinpai_describe:
							if (ret_dict.get('list') is None):
								ret_dict['list'] = []
							ret_dict['list'].append(
								{"entity1": pinpai, "rel": "故障描述", "entity2": desc[0], "entity1_type": "品牌",
								 "entity2_type": "故障描述"})

							guzhang_types = db.findOtherEntities(desc[0], "故障类型")
							selected_index = [i for i in range(len(guzhang_types))]
							for i in selected_index:
								guzhang_type = guzhang_types[i]['n2']['title']
								if (ret_dict.get('list') is None):
									ret_dict['list'] = []
								ret_dict['list'].append(
									{"entity1": desc[0], "rel": "故障类型", "entity2": guzhang_type, "entity1_type": "故障描述",
									 "entity2_type": "故障类型"})

							answers = db.findOtherEntities(desc[0], "解决方法")
							selected_index = [i for i in range(len(answers))]
							for i in selected_index:
								answer = answers[i]['n2']['title']
								if (ret_dict.get('list') is None):
									ret_dict['list'] = []
								ret_dict['list'].append(
									{"entity1": desc[0], "rel": "解决方法", "entity2": answer, "entity1_type": "故障描述",
									 "entity2_type": "解决方法"})
								if (ret_dict.get('answer') is None):
									ret_dict['answer'] = [answer]
								else:
									ret_dict['answer'].append(answer)

								if (ret_dict.get('similar') is None):
									ret_dict['similar'] = [desc[1]]
								else:
									ret_dict['similar'].append(desc[1])

		else:#找型号对应的描述
			xinghao_describe = findLikeEntitys(xinghao, '故障描述', describe)
			if len(xinghao_describe) != 0 and xinghao_describe != 0:
				for desc in xinghao_describe:
					if (ret_dict.get('list') is None):
						ret_dict['list'] = []
					ret_dict['list'].append(
						{"entity1": xinghao, "rel": "故障描述", "entity2": desc[0], "entity1_type": "型号",
						 "entity2_type": "故障描述"})
					guzhang_types = db.findOtherEntities(desc[0], "故障类型")
					selected_index = [i for i in range(len(guzhang_types))]
					for i in selected_index:
						guzhang_type = guzhang_types[i]['n2']['title']
						if (ret_dict.get('list') is None):
							ret_dict['list'] = []
						ret_dict['list'].append(
							{"entity1": desc[0], "rel": "故障类型", "entity2": guzhang_type, "entity1_type": "故障描述",
							 "entity2_type": "故障类型"})
					answers = db.findOtherEntities(desc[0], "解决方法")
					selected_index = [i for i in range(len(answers))]
					for i in selected_index:
						answer = answers[i]['n2']['title']
						if (ret_dict.get('list') is None):
							ret_dict['list'] = []
						ret_dict['list'].append(
							{"entity1": desc[0], "rel": "解决方法", "entity2": answer, "entity1_type": "故障描述",
							 "entity2_type": "解决方法"})

						if (ret_dict.get('describe') is None):
							ret_dict['describe'] = [desc[0]]
						else:
							ret_dict['describe'].append(desc[0])
						if (ret_dict.get('answer') is None):
							ret_dict['answer'] = [answer]
						else:
							ret_dict['answer'].append(answer)
						if (ret_dict.get('similar') is None):
							ret_dict['similar'] = [desc[1]]
						else:
							ret_dict['similar'].append(desc[1])
			else:#没有型号，查品牌的故障描述
				pinpai_describe = findLikeEntitys(pinpai, '故障描述', describe)
				if len(pinpai_describe) != 0 and pinpai_describe != 0:
					for desc in pinpai_describe:
						if (ret_dict.get('list') is None):
							ret_dict['list'] = []
						ret_dict['list'].append(
							{"entity1": pinpai, "rel": "故障描述", "entity2": desc[0], "entity1_type": "品牌",
							 "entity2_type": "故障描述"})
						guzhang_types = db.findOtherEntities(desc[0], "故障类型")
						selected_index = [i for i in range(len(guzhang_types))]
						for i in selected_index:
							guzhang_type = guzhang_types[i]['n2']['title']
							if (ret_dict.get('list') is None):
								ret_dict['list'] = []
							ret_dict['list'].append(
								{"entity1": desc[0], "rel": "故障类型", "entity2": guzhang_type, "entity1_type": "故障描述",
								 "entity2_type": "故障类型"})
						answers = db.findOtherEntities(desc[0], "解决方法")
						selected_index = [i for i in range(len(answers))]
						for i in selected_index:
							answer = answers[i]['n2']['title']
							if (ret_dict.get('list') is None):
								ret_dict['list'] = []
							ret_dict['list'].append(
								{"entity1": desc[0], "rel": "解决方法", "entity2": answer, "entity1_type": "故障描述",
								 "entity2_type": "解决方法"})
							if (ret_dict.get('describe') is None):
								ret_dict['describe'] = [desc[0]]
							else:
								ret_dict['describe'].append(desc[0])
							if (ret_dict.get('answer') is None):
								ret_dict['answer'] = [answer]
							else:
								ret_dict['answer'].append(answer)

							if (ret_dict.get('similar') is None):
								ret_dict['similar'] = [desc[1]]
							else:
								ret_dict['similar'].append(desc[1])




	else:#找品牌对应的故障代码
		print('找品牌对应的故障代码')
		pinpai_errorid = findEntitys(pinpai, '故障代码', errorid)
		if pinpai_errorid:
			if (ret_dict.get('list') is None):
				ret_dict['list'] = []
			ret_dict['list'].append(
				{"entity1": pinpai, "rel": "故障代码", "entity2": errorid, "entity1_type": "品牌",
				 "entity2_type": "故障代码"})
			errorid_describe = findLikeEntitys(errorid, '故障描述', describe)
			if len(errorid_describe) != 0 and errorid_describe != 0:
				for desc in errorid_describe:
					if (ret_dict.get('list') is None):
						ret_dict['list'] = []
					ret_dict['list'].append(
						{"entity1": errorid, "rel": "故障描述", "entity2": desc[0], "entity1_type": "故障代码",
						 "entity2_type": "故障描述"})
					guzhang_types = db.findOtherEntities(desc[0], "故障类型")
					selected_index = [i for i in range(len(guzhang_types))]
					for i in selected_index:
						guzhang_type = guzhang_types[i]['n2']['title']
						if (ret_dict.get('list') is None):
							ret_dict['list'] = []
						ret_dict['list'].append(
							{"entity1": desc[0], "rel": "故障类型", "entity2": guzhang_type, "entity1_type": "故障描述",
							 "entity2_type": "故障类型"})
					answers = db.findOtherEntities(desc[0], "解决方法")
					selected_index = [i for i in range(len(answers))]
					for i in selected_index:
						answer = answers[i]['n2']['title']
						if (ret_dict.get('list') is None):
							ret_dict['list'] = []
						ret_dict['list'].append(
							{"entity1": desc[0], "rel": "解决方法", "entity2": answer, "entity1_type": "故障描述",
							 "entity2_type": "解决方法"})

						if (ret_dict.get('describe') is None):
							ret_dict['describe'] = [desc[0]]
						else:
							ret_dict['describe'].append(desc[0])
						if (ret_dict.get('answer') is None):
							ret_dict['answer'] = [answer]
						else:
							ret_dict['answer'].append(answer)
						if (ret_dict.get('similar') is None):
							ret_dict['similar'] = [desc[1]]
						else:
							ret_dict['similar'].append(desc[1])
			else:
				print('没有类似的故障')#没有型号，故障代码的描述也没有，查品牌的故障描述
				pinpai_describe = findLikeEntitys(pinpai, '故障描述', describe)
				if len(pinpai_describe) != 0 and pinpai_describe != 0:
					for desc in pinpai_describe:
						if (ret_dict.get('list') is None):
							ret_dict['list'] = []
						ret_dict['list'].append(
							{"entity1": pinpai, "rel": "故障描述", "entity2": desc[0], "entity1_type": "品牌",
							 "entity2_type": "故障描述"})
						guzhang_types = db.findOtherEntities(desc[0], "故障类型")
						selected_index = [i for i in range(len(guzhang_types))]
						for i in selected_index:
							guzhang_type = guzhang_types[i]['n2']['title']
							if (ret_dict.get('list') is None):
								ret_dict['list'] = []
							ret_dict['list'].append(
								{"entity1": desc[0], "rel": "故障类型", "entity2": guzhang_type, "entity1_type": "故障描述",
								 "entity2_type": "故障类型"})
						answers = db.findOtherEntities(desc[0], "解决方法")
						selected_index = [i for i in range(len(answers))]
						for i in selected_index:
							answer = answers[i]['n2']['title']
							if (ret_dict.get('list') is None):
								ret_dict['list'] = []
							ret_dict['list'].append(
								{"entity1": desc[0], "rel": "解决方法", "entity2": answer, "entity1_type": "故障描述",
								 "entity2_type": "解决方法"})

							if (ret_dict.get('describe') is None):
								ret_dict['describe'] = [desc[0]]
							else:
								ret_dict['describe'].append(desc[0])
							if (ret_dict.get('answer') is None):
								ret_dict['answer'] = [answer]
							else:
								ret_dict['answer'].append(answer)

							if (ret_dict.get('similar') is None):
								ret_dict['similar'] = [desc[1]]
							else:
								ret_dict['similar'].append(desc[1])
		else:#品牌对应的描述
			print('品牌对应的描述')
			pinpai_describe = findLikeEntitys(pinpai, '故障描述', describe)
			if len(pinpai_describe) != 0 and pinpai_describe != 0:
				for desc in pinpai_describe:
					if (ret_dict.get('list') is None):
						ret_dict['list'] = []
					ret_dict['list'].append(
						{"entity1": pinpai, "rel": "故障描述", "entity2": desc[0], "entity1_type": "品牌",
						 "entity2_type": "故障描述"})
					guzhang_types = db.findOtherEntities(desc[0], "故障类型")
					selected_index = [i for i in range(len(guzhang_types))]
					for i in selected_index:
						guzhang_type = guzhang_types[i]['n2']['title']
						if (ret_dict.get('list') is None):
							ret_dict['list'] = []
						ret_dict['list'].append(
							{"entity1": desc[0], "rel": "故障类型", "entity2": guzhang_type, "entity1_type": "故障描述",
							 "entity2_type": "故障类型"})
					answers = db.findOtherEntities(desc[0], "解决方法")
					selected_index = [i for i in range(len(answers))]
					for i in selected_index:
						answer = answers[i]['n2']['title']
						if (ret_dict.get('list') is None):
							ret_dict['list'] = []
						ret_dict['list'].append(
							{"entity1": desc[0], "rel": "解决方法", "entity2": answer, "entity1_type": "故障描述",
							 "entity2_type": "解决方法"})

						if (ret_dict.get('describe') is None):
							ret_dict['describe'] = [desc[0]]
						else:
							ret_dict['describe'].append(desc[0])

						if (ret_dict.get('answer') is None):
							ret_dict['answer'] = [answer]
						else:
							ret_dict['answer'].append(answer)

						if (ret_dict.get('similar') is None):
							ret_dict['similar'] = [desc[1]]
						else:
							ret_dict['similar'].append(desc[1])
	if(len(ret_dict)==0 or ret_dict == 0):
		print('找所有的描述')
		dbdescribes = db.findAllDescribes()
		selected_index = [i for i in range(len(dbdescribes))]
		describelist = []
		for i in selected_index:
			describelist.append(dbdescribes[i]['m']['title'])
		similar_describe = findSimilarEntitys(describe,describelist)
		if len(similar_describe) != 0 and similar_describe != 0:
			i = 0
			for desc in similar_describe:
				i = i + 1
				if i>7:
					break
				guzhang_types = db.findOtherEntities(desc[0], "故障类型")
				selected_index = [i for i in range(len(guzhang_types))]
				for i in selected_index:
					guzhang_type = guzhang_types[i]['n2']['title']
					if (ret_dict.get('list') is None):
						ret_dict['list'] = []
					ret_dict['list'].append(
						{"entity1": desc[0], "rel": "故障类型", "entity2": guzhang_type, "entity1_type": "故障描述",
						 "entity2_type": "故障类型"})
				answers = db.findOtherEntities(desc[0], "解决方法")
				selected_index = [i for i in range(len(answers))]
				for i in selected_index:
					answer = answers[i]['n2']['title']
					if (ret_dict.get('list') is None):
						ret_dict['list'] = []
					ret_dict['list'].append(
						{"entity1": desc[0], "rel": "解决方法", "entity2": answer, "entity1_type": "故障描述",
						 "entity2_type": "解决方法"})

					if (ret_dict.get('describe') is None):
						ret_dict['describe'] = [desc[0]]
					else:
						ret_dict['describe'].append(desc[0])
					if (ret_dict.get('answer') is None):
						ret_dict['answer'] = [answer]
					else:
						ret_dict['answer'].append(answer)

					if (ret_dict.get('similar') is None):
						ret_dict['similar'] = [desc[1]]
					else:
						ret_dict['similar'].append(desc[1])
	return ret_dict
def question_answering():  # index页面需要一开始就加载的内容写在这里
	ret_dict = {}
	pinpai = '广州数控'
	xinghao = 'GSK988T'
	errorid = '1'
	question = '零件程序打开失败'
	relationList = []
	ret_dict = getTuili(pinpai, xinghao, errorid, question, relationList, ret_dict)
	if (ret_dict.get('list') is not None):
		return json.dumps(ret_dict, ensure_ascii=False)
	else:
		ret_dict = get_answer(pinpai, xinghao, errorid, question, ret_dict)
	if (ret_dict.get('list') is not None):
		return json.dumps(ret_dict, ensure_ascii=False)
	return json.dumps('没有找到类似的答案', ensure_ascii=False)


if __name__ == '__main__':
	print(question_answering())