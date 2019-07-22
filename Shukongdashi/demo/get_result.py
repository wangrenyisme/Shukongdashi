# coding: utf-8
import json
import os
from Shukongdashi.demo import question_pa

question_list = []
with open('../label_data/a.txt', 'r', encoding='utf8') as fr:
    for question in fr.readlines():
        question_list.append(question.strip())
# question_list = ['+24V负载短路','连接单元故障','控制ROM板不良']
file = open("result.txt", 'a+', encoding='utf-8')
for q in question_list:
    print(type(q))
    print(q)
    # file.write(q.strip() + ',' + '解决办法,无\n')
    try:
        temp = question_pa.main(q.strip())
        jsonTmp = json.loads(temp)
        tmp = jsonTmp['answer']
        try:
            file.write('"' + tmp[0]['answer'] + '"\n')
            print(tmp[0]['answer'])

            # line = tmp[0]['answer']
            # data = ''.join(re.findall(u'[a-zA-Z\u4e00-\u9fa5]+', line.decode('utf-8', 'ignore')))
            # file.write('"' + data + '"\n')
        except:
            print('查找失败')
    except:
        print('查找失败')

file.close()
