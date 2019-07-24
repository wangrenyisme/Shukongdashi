
# Shukongdashi
使用知识图谱，自然语言处理，卷积神经网络等技术，基于python语言，设计了一个数控领域故障诊断专家系统

## 项目介绍
本项目是第八届中国软件杯大赛，基于移动端在线设备故障诊断平台的参赛作品。\
数控机床故障诊断和维修是企业设备管理的难点和重点，设备在运行中会产生各种“疑难杂症”，不及时排出就会影响生产生活，甚至酿成事故。数控机床出了故障，一旦查清了故障点和故障原因，维修起来其实是一件比较容易的事。通过自适应设备故障诊断APP，根据故障信息，自动抓取互联网中适应的故障产生原因和优秀解决方法，形成知识库，将辅助设备维修人员快速诊断排出故障，保障生产。
>团队名称：集结号\
>指导教师：王建民\
>团队成员：王任义、王金萱、马佳慧
## 目录结构
    ├── Shukongdashi
        └── demo
            ├── checkpoints //存放CNN的训练模型
            ├── data    //CNN预测辅助代码和文件
                ├── cnews   //使用CNN预测用到的词
                └── cnews_loader.py    //为数据的预处理文件
            ├── fencidian.txt   //分词词典
            ├── question_answer.py  //第一版故障诊断代码（已弃用）
            ├── question_baocun.py  //处理用户反馈的代码
            ├── question_buquan.py  //自动补全代码
            ├── question_pa.py  //在线分析性代码，爬取解决方法
            ├── question_wenda.py  //问答功能
            ├── question_zhenduan.py  //故障诊断代码
            ├── stopwords.txt  //停用词词典
            └── zhuyu.txt  //故障部位词典
        ├── Model
            └── neo_models.py  //执行neo4j数据库操作
        ├── test_my
            ├── data_wordToMysql  //将word中的数据转换成csv文件，存储到MySQL中
            ├── test_cnnrnn  //CNN卷积神经网络预测
                ├── checkpoints  //存储训练模型
                ├── data  //数据的预处理文件
                ├── neo4j  //导入Neo4j的数据
                    ├── baojing.csv  //故障代码
                    ├── caozuo.csv  //执行的操作
                    ├── caozuoxianxaing.csv  //由于执行某操作引起了某现象
                    ├── xianxaingbaojing.csv  //某现象对应的报警信息
                    ├── xianxaingbuwei.csv  //某现象对应的故障部位
                    ├── xianxiang.csv  //故障现象
                    ├── xianxiangxianxiang.csv  //故障现象和故障现象之间的关联关系
                    ├── xianxiangyuanyin.csv  //故障现象的间接故障原因
                    ├── yuanyin2.csv  //故障原因
                    └── zhuyu.csv  //故障部位
                ├── cnn_model.py  //CNN配置
                ├── guzhangfenxi.py  //构建Neo4j数据库用的数据
                └── predict.py  //CNN预测识别故障描述类型
            └── xianxiangfenxi  //故障部位词典
                ├── baojing.csv  //对故障现象进行拆分，抽取出故障部位，故障现象，故障发生的背景，手动标记后进一步标注含义
                ├── biaozhu_minming.txt //标注好的数据，用于训练CNN模型
                └── guzhangxianxiang.csv    //用于分析的故障现象文件
        ├── toolkit
            └── pre_load.py //预加载训练模型和Neo4j数据库，还可以对读取词典进行预加载，进行性能优化
        ├── settings.py //配置访问端口等
        ├── urls.py //配置URL与python函数的映射
        ├── view.py //默认页面
        └── wsgi.py
    ├── db.sqlite3
    └── manage.py   //Django框架项目启动入口
## 项目配置
### 0.安装基本环境：
确保安装好python3和Neo4j（任意版本）\
安装一系列pip依赖：
### 1.导入数据：
开启neo4j，进入neo4j控制台。将Shukongdashi/test_my/test_cnnrnn/neo4/下的文件放入neo4j安装目录下的/import目录。在控制台依次输入：

    //导入节点
    LOAD CSV WITH HEADERS FROM "file:///baojing.csv" AS line MERGE (:Errorid { title: line.title });
    CREATE CONSTRAINT ON (c:Errorid) ASSERT c.title IS UNIQUE;
    LOAD CSV WITH HEADERS FROM "file:///caozuo.csv" AS line MERGE (:Caozuo { title: line.title });
    CREATE CONSTRAINT ON (c:Caozuo) ASSERT c.title IS UNIQUE;
    LOAD CSV WITH HEADERS FROM "file:///xianxiang.csv" AS line MERGE (:Xianxiang { title: line.title });
    CREATE CONSTRAINT ON (c:Xianxiang) ASSERT c.title IS UNIQUE;
    LOAD CSV WITH HEADERS FROM "file:///zhuyu.csv" AS line MERGE (:GuzhangBuwei { title: line.title });
    CREATE CONSTRAINT ON (c:GuzhangBuwei) ASSERT c.title IS UNIQUE;
    LOAD CSV WITH HEADERS FROM "file:///yuanyin2.csv" AS line MERGE (:Yuanyin { title: line.title });
    CREATE CONSTRAINT ON (c:Yuanyin) ASSERT c.title IS UNIQUE;
        //导入关系
    LOAD CSV  WITH HEADERS FROM "file:///caozuoxianxaing.csv" AS line MATCH (entity1 {title:line.title1}),(entity2 {title:line.title2}) CREATE (entity1)-[:CX { type: line.relation }]->(entity2)
    LOAD CSV  WITH HEADERS FROM "file:///xianxiangyuanyin.csv" AS line MATCH (entity1 {title:line.title1}),(entity2 {title:line.title2}) CREATE (entity1)-[:XY { type: line.relation }]->(entity2)
    LOAD CSV  WITH HEADERS FROM "file:///xianxiangxianxiang.csv" AS line MATCH (entity1 {title:line.title1}),(entity2 {title:line.title2}) CREATE (entity1)-[:XX { type: line.relation }]->(entity2)
    LOAD CSV  WITH HEADERS FROM "file:///xianxaingbuwei.csv" AS line MATCH (entity1 {title:line.title1}),(entity2 {title:line.title2}) CREATE (entity1)-[:XB { type: line.relation }]->(entity2)
    LOAD CSV  WITH HEADERS FROM "file:///xianxaingbaojing.csv" AS line MATCH (entity1 {title:line.title1}),(entity2 {title:line.title2}) CREATE (entity1)-[:XJ { type: line.relation }]->(entity2)
### 2.修改Neo4j用户
进入Shukongdashi/Model/neo_models.py,修改第8行的neo4j账号密码，改成你自己的
### 3.启动服务
进入项目根目录，然后运行脚本：

    python manage.py runserver 0.0.0.0:8000
## 系统功能
构建的知识图谱效果如下图所示：\
![知识图谱](https://github.com/wangrenyisme/Shukongdashi/tree/master/image/zhishiku.png)

## 设计思路

通过学习大量数控机床的历史维修案例，基于知识图谱、自然语言处理技术，融合规则推理，我们设计了一个越用越聪明的诊断数控机床故障专家系统。\
首先，我们爬取了大量数控机床维修案例，使用NLP自然语言处理技术对文本做了噪声移除和句法分析，然后使用CNN卷积神经网络识别出了故障描述中用户所做的操作和出现的故障现象，结合词性标注，正则表达式处理等技术，最终提取出了故障描述中，对机床执行的操作，故障的现象，故障的部位，存在的报警信号。\
基于Neo4j图数据库能够清晰的表示数据模型的优点，我们经过上面对故障描述的拆分和标注，表示出了做了什么操作会引起了什么故障现象，故障现象之间的并发或间接导致的关联关系，一个故障原因会间接或直接导致哪些故障现象的发生，机床的某个部位会出现的故障现象，报警代码和故障现象之间的关联，构成了知识图谱，使用基于规则的推理模型实现了我们的推理算法。\
当一个新的故障发生时，通过分析，如果现有的知识不能解决新的故障，这时通过在线分析，爬取解决方案，通过用户人为反馈和语料库对比分析程序，确认结果可靠之后，分析当前的故障描述，原理同上述构建知识库的过程，拆分之后，对新的知识进行补充，对已经存在的知识，进一步完善和优化，最终实现知识库的自学习功能。\
在故障诊断的过程中，类似上述的处理方法，分析故障描述，通过分析故障部位，出现的现象，所做的操作，结合知识图谱，分析出导致这些现象出现的最可能的故障原因，设置权值，然后通过CNN卷积神经网络对故障现象进行预测，对诊断出的故障结果的权值进行微调，排序之后展示给用户。
