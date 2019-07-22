# coding: utf-8
import jieba
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
import os
import difflib
from lxml import etree   #导入Lxml中的etree库
import requests
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
        print(response.status_code)
        # print(response.text)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_page(url,page):
    for i in range(1,int(page)+1):
        #print("正在爬取第{}页....".format(i))
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
                print("无更多页面！～")
                return
            yield data

#下面的函数是读取上面爬出来的内容并做处理
def readjsonAndsort(ret_dict):
    bd = []  # 存储百度知道
    d = {}
    nobd = []  # 存储非百度知道的内容
    sumallzd = 0  # 用于控制得到的优先性高的评论只输出前五条
    with open(os.getcwd()+"\\Shukongdashi\\demo\\data.json", 'rb') as f:
      temp = json.loads(f.read())
      #print('===================================================================================================爬取的所有内容')
      ret_dict['simple_url'] = []
      ret_dict['answer'] = []
      for tp in temp:#解析json数据
          str = tp['title'] + ',' + tp['sub_url']
          #print(str)
          if '_百度知道' in tp['title']:
              str=tp['sub_url']
              bd.append(str)
          else:
              ret_dict['simple_url'].append(
                  {"title": tp['title'], "sub_url": tp['sub_url']})
              nobd.append(str)#其他相似性问题及连接的数组
    # print('--------------------------------------------------------------------------------------------------------其他相似性的链接')
    # for nb in nobd:
    #     print(nb)
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
                sumallzd+=1
                if sumallzd<5:
                    addWord(d, content[connum], zan[connum*2])#控制在5条以内
        connum=0
    if len(bd)!=0:
        res=sorted(d.items(),key=lambda d:d[1],reverse=True)
        for value in res:
            ret_dict['answer'].append({'answer': value[0],'zan':value[1][0]})
        #print('---------------------------------------------------------------------------------------------------------百度知道内容优先级排序后的评论输出')
        #ret_dict['answer']=res
        #print(ret_dict)#可以进行特定的输出 如res[1]
        #print('*************************************************************************************************************************************')
    else:
        ret_dict['answer'].append({'answer': '首先检查气液转换的气源压力正常,检查工作台压紧液压缸油位 指示杆，已到上限，可能缺油，用螺钉旋具拧工作台上升、下落电磁阀手动钮，让工作台 压紧气液转换缸补油，油位指示杆回到中间位置，报警消除。但过半小时左右，报警又 出现,再查压紧液压缸油位，又缺油，故怀疑油路有泄漏。查油管各接头正常，怀疑对象 缩小为工作台夹紧工作液压缸和夹紧气液转换缸，查气液转换缸，发现油腔端Y形聚胺 酯密封有裂纹，导致压力油慢慢回流到补油腔，最后因油不够不能形成油压而报警，更 换后故障排除。','zan':10})
        ret_dict['answer'].append({'answer': '现场观察，主轴处于非定向状态，可以断定换刀过程中，定向偏 移,卡住;而根据报警号分析，说明主轴试图恢复到定向位置，但因卡住面报警关机。手 动操作电磁闹分别将主轴刀具松开，刀库伸出，手工将刀爪上的刀卸下，再手动将主轴 夹紧，刀库退回；开机，报警消除。为查找原因，检查刀库刀爪与主轴相对位置，发现刀 库刀爪偏左，主轴换刀后下移时刀爪右指刮擦刀柄，造成主轴顺时针转动偏离定向，而 主轴默认定向为M19,恢复定向旋转方向与偏离方向一致，更加大了这一偏离，因而偏 离很多造成卡死;而主轴上移时，刀爪右指刮擦使刀柄逆转，而M19定向为正转正好将 其消除，不存在这一问题。调整刀库四零位置参数7508,使刀爪与主轴对齐后，故障消除。','zan':8})
        ret_dict['answer'].append({'answer': '使用时间较长, 液压站的输出压力调得太高，导致联轴器的啮合齿损坏，从而当液压电动机旋转时，联 轴器不能很好地传递转矩，从而产生异响。更换该联轴器后，机床恢复正常。','zan':6})
        print('未搜索到您的问题！来看看相似问题吧！')
    try:#读完之后对文件进行删除 下一次查询不一样的问题生成的答案会不一样 相当于更新了data.json
        os.remove( 'data.json' )
    except  WindowsError:
        pass
    return ret_dict
def lists_combination(lists, code=''):
    '''输入多个列表组成的列表, 输出其中每个列表所有元素可能的所有排列组合
    code用于分隔每个元素'''
    try:
        import reduce
    except:
        from functools import reduce

    def myfunc(list1, list2):
        return [str(i) + code + str(j) for i in list1 for j in list2]

    return reduce(myfunc, lists)

def main(request):#主操作函数
    if (request.GET):
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
        if errorid != '':
            question += '，' + errorid + '报警'
        jieba.load_userdict(os.getcwd() + '\\Shukongdashi\\demo\\fencidian.txt')
        pattern = r'\.|;|。|；|！'
        pattern2 = r',|，'

        # 加载停用词
        stopwords = []
        with open(os.getcwd() + '\\Shukongdashi\\demo\\stopwords.txt', 'r', encoding='utf-8') as f:
            st = f.readlines()
        for line in st:
            line = line.strip().encode('utf-8').decode('utf-8-sig')
            stopwords.append(line)
        # 加载故障部位
        buweizhuyu = []
        with open(os.getcwd() + '\\Shukongdashi\\demo\\zhuyu.txt', 'r', encoding='utf-8') as f:
            st = f.readlines()
        for line in st:
            line = line.strip().encode('utf-8').decode('utf-8-sig')  # 防止BOM现象
            buweizhuyu.append(line)
        miaoshu = question.replace(' ', '')
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
        print('执行操作:', miaoshu_caozuo)
        print('故障现象:', miaoshu_xianxiang)
        ques = []
        if pinpai != '':
            if len(miaoshu_caozuo)>0:
                if len(miaoshu_xianxiang)>0:
                    ques = lists_combination([pinpai,miaoshu_caozuo, miaoshu_xianxiang], ',')
                else:
                    ques = lists_combination([pinpai, miaoshu_caozuo], ',')
            else:
                if len(miaoshu_xianxiang)>0:
                    ques = lists_combination([pinpai, miaoshu_xianxiang], ',')
        else:
            if len(miaoshu_caozuo)>0:
                if len(miaoshu_xianxiang)>0:
                    ques = lists_combination([miaoshu_caozuo, miaoshu_xianxiang], ',')
                else:
                    ques = ','.join(miaoshu_caozuo)
            else:
                if len(miaoshu_xianxiang)>0:
                    ques = ','.join(miaoshu_xianxiang)
        ret_dict={}
        for que in ques:
            if (ret_dict.get('answer') is None):
                page = 1
                url = get_url(que)
                results = parse_page(url, page)
                # 写入文件
                file = open(os.getcwd()+"\\Shukongdashi\\demo\\data.json", 'w+', encoding='utf-8')
                file.write('[\n')
                zan = []
                i = 0
                # print('爬取的所有内容：')
                for result in results:
                    # print(result)
                    zan.append(result)  # j现将迭代器遍历一遍存入数组 求其长度 方便后续json文件加逗号
                    # file.write(json.dumps(result, indent=2, ensure_ascii=False))
                for m in zan:
                    file.write(json.dumps(m, indent=2, ensure_ascii=False))  # 生成了完整的json
                    if i != len(zan) - 1:
                        file.write(',')
                    i += 1
                file.write('\n]')
                file.close()
                ret_dict = readjsonAndsort(ret_dict)  # 调取解析json并对数据进行二次处理的函数
            else:
                break

        if (len(ret_dict) != 0 and ret_dict != 0):
            return HttpResponse(json.dumps(ret_dict, ensure_ascii=False), content_type="application/json;charset=utf-8")
        else:

            return HttpResponse(json.dumps('没有找到相关答案', ensure_ascii=False), content_type="application/json;charset=utf-8")
    else:
        return HttpResponse(json.dumps('没有找到相关答案', ensure_ascii=False), content_type="application/json;charset=utf-8")
