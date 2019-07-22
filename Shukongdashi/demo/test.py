from Shukongdashi.toolkit.pre_load import neo_con

insertTwoNodes(sentence, '报警信息', x.word, 'Xianxiang', 'Errorid')









# def lists_combination(lists, code=''):
#     '''输入多个列表组成的列表, 输出其中每个列表所有元素可能的所有排列组合
#     code用于分隔每个元素'''
#     try:
#         import reduce
#     except:
#         from functools import reduce
#
#     def myfunc(list1, list2):
#         return [str(i) + code + str(j) for i in list1 for j in list2]
#
#     return reduce(myfunc, lists)
#
#
# list1 = [1, 2]
# list2 = [3, 4]
# list3 = [5, 6]
#
#
# res = lists_combination([[1],  list3],',')
# print(res)
# # 最终结果为:

# import requests
#
# import json
#
# import base64
#
# import socket
#
#
# # 首先将图片读入
#
# # 由于要发送json，所以需要对byte进行str解码
#
# def getByte(path):
#     with open(path, 'rb') as f:
#         img_byte = base64.b64encode(f.read())
#
#     img_str = img_byte.decode('ascii')
#
#     return img_str
#
#
# img_str = getByte('test.png')
#
#
# # 此段为获得ip，本人使用本机服务器测试
#
# def getIp():
#     try:
#
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#
#         s.connect(('127.0.0.1', 8000))
#
#         ip = s.getsockname()[0]
#
#     finally:
#
#         s.close()
#
#     return ip
#
#
# url = 'http://' + str(getIp()) + ':8000/img'
#
# data = {'images': img_str}
#
# json_mod = json.dumps(data)
#
# res = requests.post(url=url, data=json_mod)
#
# print(res.text)
#
# # 如果服务器没有报错，传回json格式数据
#
# print(eval(res.text))
