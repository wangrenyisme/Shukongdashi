import requests
import urllib.parse

from django.http import HttpResponse
from requests.exceptions import RequestException
from urllib.parse import urljoin
import re
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen
import sys
import io
import  os
import difflib
from lxml import etree   #导入Lxml中的etree库
import requests
import jieba.posseg
import jieba
from Shukongdashi.toolkit.pre_load import cnn_model
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
cnnModel = cnn_model
# 百度搜索接口
def addWord(theIndex, word, pagenumber):#自定义字典添加函数
    theIndex.setdefault(word, [ ]).append(pagenumber)  # 存在就在基础上加入列表，不存在就新建个字典key
def format_url(url, params: dict=None) -> str:#爬取百度接口
    query_str = urllib.parse.urlencode(params)
    return f'{ url }?{ query_str }'
def get_url(keyword):
    params = {
        'wd': str(keyword)
    }
    url = "https://www.baidu.com/s"
    url = format_url(url, params)
    # print(url)

    return url

def get_page(url):
    try:
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
        }
        response = requests.get(url=url,headers=headers)
        # 更改编码方式，否则会出现乱码的情况
        response.encoding = "utf-8"
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_page(url,page):
    for i in range(1,int(page)+1):
        title = ""
        sub_url = ""
        abstract = ""
        flag = 11
        if i == 1:
            flag = 10
        html = get_page(url)
        content = etree.HTML(html)
        for j in range(1,flag):
            data = {}
            res_title = content.xpath('//*[@id="%d"]/h3/a' % ((i - 1) * 10 + j))
            if res_title:
                title = res_title[0].xpath('string(.)')

            sub_url = content.xpath('//*[@id="%d"]/h3/a/@href' % ((i - 1) * 10 + j))
            if sub_url:
                sub_url = sub_url[0]

            res_abstract = content.xpath('//*[@id="%d"]/div[@class="c-abstract"]'%((i-1)*10+j))
            if res_abstract:
                abstract = res_abstract[0].xpath('string(.)')
            else:
                res_abstract = content.xpath('//*[@id="%d"]/div/div[2]/div[@class="c-abstract"]'%((i-1)*10+j))
                if res_abstract:
                    abstract = res_abstract[0].xpath('string(.)')
                    # res_abstract = content.xpath('//*[@id="%d"]/div/div[2]/p[1]'%((i-1)*10+j))
            # if not abstract:
            #     abstract = content.xpath('//*[@id="%d"]/div/div[2]/p[1]'%((i-1)*10+j))[0].xpath('string(.)')
            data['title'] = title
            data['sub_url'] = sub_url
            data['abstract'] = abstract


            rel_url = content.xpath('//*[@id="page"]/a[{}]/@href'.format(flag))
            if rel_url:
                url = urljoin(url, rel_url[0])
            else:
                return
            yield data

#下面的函数是读取上面爬出来的内容并做处理
def readjsonAndsort():
    info_sim = {}
    ans_json = {}
    list_ans = {}
    data_all = {}
    list_ans = []
    list_sim = []#后续输出的json格式的内容用到的
    bd = []  # 存储百度知道
    d = {}
    lgson=0#控制只输出最好的五条解决方案
    dic={}#用来存储评论
    nobd = []  # 存储非百度知道的内容
    sumallzd = 0  # 用于控制得到的优先性高的评论只输出前五条
    with open(os.getcwd()+"\\Shukongdashi\\demo\\data.json", 'rb') as f:
      temp = json.loads(f.read())
      select_sim=0
      select_simnum=0
      for tp in temp:#解析json数据
          str = tp['title'] + ',' + tp['sub_url']
          if '_百度知道' in tp['title']:
              str=tp['sub_url']
              bd.append(str)
          else:
              if select_sim%2==0:
                  if select_simnum<5:
                      info_sim = {}
                      info_sim["title"] = tp['title']
                      info_sim["sub_url"] = tp['sub_url']
                      list_sim.append(info_sim)
                      select_simnum = select_simnum + 1
              select_sim=select_sim+1

              nobd.append(str)#其他相似性问题及连接的数组


    for ur in bd:#遍历所有的百度知道
        content = []  # 存储评论的数组 只爬取一页评论
        url = ur
        html = urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")
        titles01 = soup.select("div [class='best-text mb-10'] ")  # CSS 选择器 这是爬取第一个评论 第一个评论和其他评论标签不一样
        for tit in titles01:
            content.append(re.sub('[\n]+', '\n', tit.get_text()[8:]).strip())#去掉空格和换行去掉前几个不需要字
        titles = soup.select("div [class='answer-text mb-10 line'] ")  # CSS 选择器 爬取第二个评论
        for title in titles:
            content.append(re.sub('[\n]+', '\n', title.get_text()[8:]).strip())
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        }
        html = requests.get(url,headers = headers)
        html.encoding = 'gbk'
        selector = etree.HTML(html.text)
        zan = selector.xpath('//*[@id="qb-content"]//span/@data-evaluate')  #取大标签，以此循环
        for connum in range(len(content)):
            if int(zan[connum*2])>0:#将评论里有赞的评论挑选出来作为结果集
                #sumallzd+=1
                #if sumallzd<5:
                dic.setdefault(content[connum],int(zan[connum*2]))
                    #addWord(d, content[connum], zan[connum*2])#控制在5条以内
                sumallzd += 1
    if len(dic)!=0:
        #res=sorted(d.items(),key=lambda d:d[1],reverse=True)
        import operator
        res=sorted(dic.items(), key=lambda item: item[1])
        for lg in range(int(len(res))):
            if lgson<5:
                #print(res[0][1])
                print(res[len(res)-(lg+1)])#可以进行特定的输出 如res[1]
                ans_json = {}
                ans_json['answer']=res[len(res)-(lg+1)][0]
                ans_json['zan']=res[len(res)-(lg+1)][1]
                list_ans.append(ans_json)
            lgson=lgson+1
    else:
        print('未搜索到您的问题！来看看相似问题吧！')
    data_all["simple_url"] = list_sim
    data_all["answer"] = list_ans
    print(data_all)#这是最后得到的json数据
    try:#读完之后对文件进行删除 下一次查询不一样的问题生成的答案会不一样 相当于更新了data.json
        pass
    except  WindowsError:
        pass
    os.remove(os.getcwd()+"\\Shukongdashi\\demo\\data.json")
    return data_all

def lists_combination(lists, code=''):
    '''输入多个列表组成的列表, 输出其中每个列表所有元素可能的所有排列组合
    code用于分隔每个元素'''
    try:
        import reduce
    except:
        from functools import reduce

def main(pinpai, xinghao, errorid, describe, relationList, ret_dict):
    print('os.getcwd():',os.getcwd())
    #keyword = input("输入关键字:")
    if errorid!='':
        describe += '，' + errorid + '报警'
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
    print('执行操作:',miaoshu_caozuo)
    print('故障现象:',miaoshu_xianxiang)
    ques = []
    for xianxiang in miaoshu_xianxiang:
        ques.append(pinpai+xianxiang)
    # ques=[pinpai+describe,errorid+describe]
    print('ques:',ques)
    zan = []
    page = 1

    file = open(os.getcwd()+"\\Shukongdashi\\demo\\data.json", 'w+', encoding='utf-8')
    file.write('[\n')
    lgt=0
    for que in ques:
        url = get_url(que)
        results = parse_page(url,page)
        # 写入文件
        zannum = 0
        for result in results:
            zan.append(result)#j现将迭代器遍历一遍存入数组 求其长度 方便后续json文件加逗号
            #file.write(json.dumps(result, indent=2, ensure_ascii=False))
        for m in zan:
            file.write(json.dumps(m, indent=2, ensure_ascii=False))#生成了完整的json
            if lgt==len(ques)-1:
                if zannum!=len(zan)-1:
                    file.write(',')
            else:
                file.write(',')
            zannum=zannum+1
        lgt=lgt+1

    file.write('\n]')
    file.close()
    return readjsonAndsort()#调取解析json并对数据进行二次处理的函数

def question_pa(request):  # index页面需要一开始就加载的内容写在这里
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
            ret_dict = main(pinpai, xinghao, errorid, question, relationList, ret_dict)
        if (ret_dict.get('simple_url') is not None):
            return HttpResponse(json.dumps(ret_dict, ensure_ascii=False), content_type="application/json;charset=utf-8")
        else:
            return HttpResponse(json.dumps('没有找到类似的答案', ensure_ascii=False), content_type="application/json;charset=utf-8")
    else:
        return HttpResponse(json.dumps("没有参数的请求", ensure_ascii=False))
