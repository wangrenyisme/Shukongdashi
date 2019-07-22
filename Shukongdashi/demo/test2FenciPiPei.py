import sys
# coding:utf-8
import pandas as pd
import pymysql


conn = pymysql.connect(host='localhost', user='root', passwd='root', db='Shukong', port=3306, charset='utf8')
cursor = conn.cursor()  # 光标对象
from Word2Vec import Word2Vec
import jieba

def load(tableItem): # 单表查询全部内容
    # 获取故障信息及解决方案
    sql = "select * from " + tableItem
    cursor.execute(sql)
    results = cursor.fetchall()
    result = list(results)
    return result



def pipei(userInput):
    w2v = Word2Vec('./wiki_chinese_word2vec(Google).model', kind='bin')

    '''停用词的过滤'''
    typetxt = open('./停用词.txt', encoding='utf-8')  # encoding默认是gbk
    stopwords = ['\u3000', '\n', ' ']  # 爬取的文本中未处理的特殊字符
    '''停用词库的建立'''
    for word in typetxt:
        word = word.strip()
        stopwords.append(word)

    # 这个是提取用户输入的关键词，试过了，很多该提取出来的词他都没有，做的不准，所以不用这个，直接对用户输入分词然后去停用词
    # import codecs
    # from textrank4zh import TextRank4Keyword, TextRank4Sentence
    #
    # tr4w = TextRank4Keyword()
    # tr4w.analyze(text=userInput, lower=True, window=2)   # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象
    #
    # print( '关键词：' )
    # keywords = tr4w.get_keywords(6, word_min_len=1)
    # key = []
    # for item in keywords:
    #     print(item.word, item.weight)
    #     key.append(item.word)
    # print(key)
    # 关键词提取结束

    s1 = userInput
    wordList1 = list(jieba.cut(s1))
    print(wordList1)
    for fenci in wordList1:
        for stop in stopwords:
            if stop == fenci:
                wordList1.remove(fenci)
    print(wordList1)

    tableName = ['gsk', 'huanum', 'mitsubishi', 'rexroth', 'publicinfor','public']
    result = {}  # 用于存储从数据库中取出来的全部数据
    dictionary = {}  # 用于计算相似度后，把解决方案、对应id、相似度存入字典，根据相似度大小逆序输出

    if '广州数控' in userInput or 'GSK' in userInput or 'gsk' in userInput:
        result = load('gsk')
    elif '华中数控' in userInput or 'huanum' in userInput:
        result = load('huanum')
    elif '三菱' in userInput or 'mitsubishi' in userInput or 'MITSUBISHI' in userInput:
        result = load('mitsubishi')
    elif '力士乐' in userInput or 'rexroth' in userInput:
        result = load('rexroth')
    else:
        for i in range(0, len(tableName)):
            result = load(tableName[i])

    for item in result:
        print('****', item)
        id = item[0]
        errorid = item[1]
        describeSys = item[2]
        answer = item[3]
        type = item[4]

        if errorid != None and errorid != '':
            describeSys = item[1] + ' ' + describeSys
        if type != '暂无分类' and type != None:
            describeSys += ' ' + type
        print(describeSys)

        flag = 0  # 如果知识库的信息里包含用户问题的分词 value置1，否则为0
        for key in wordList1:
            if key in describeSys:
                flag = 1
                break

        if flag == 0:
            pass
        if flag == 1:
            print('you----', item)

            s2 = describeSys
            wordList2 = list(jieba.cut(s2))

            similar = str(w2v.sentence_similarity(wordList1, wordList2))
            print("s1|s2: " + similar)

            dictionary.update({(id, describeSys, answer): similar})  # 将id，描述，解决方法，以及对应的相似度加入字典
            print(dictionary)
            print('*' * 30, len(dictionary))

    print('======================================================================')
    dictionary = sorted(dictionary.items(), key=lambda item: item[1], reverse=True)  # 对字典根据相似度进行降序排序
    print(dictionary)
    answersListDict = []  # 最终展示前5个(字典类型)
    # print(sorted(dictionary.items(), key=lambda item: item[1], reverse=True))
    for i in range(0, len(dictionary)):
        if i >= 5:
            break
        print(dictionary[i])
        answersListDict.append(dictionary[i])
        print('相似度：', dictionary[i][1])
        print('分析和解决方案：', dictionary[i][0][2])
        print('------------------------------------------------')

    print('answersListDict----', len(answersListDict), answersListDict)

    # for answerItem in dictionary:
    #     print(answerItem)
    #     print('相似度：', answerItem[1])
    #     print('分析和解决方案：',answerItem[0][2])
    #     print('------------------------------------------------')

    print('共', len(dictionary), '个方案')




userInput = input('请输入您遇到的故障：')
pipei(userInput)
