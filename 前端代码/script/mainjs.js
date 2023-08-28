var resultData = '';//全局的数据
$(function(){
    resultData = data;
    histogram('histogramParent__zhexian', resultData.monthSalsePickPrePart[0]);
});


function histogram(id, obj) {
    var yearList = [], qtyList = [];//年份，重量集合
    var color = "#92DCFB";
    for (var i in obj.detail) {
        yearList.push(obj.detail[i].title);
        qtyList.push(obj.detail[i].value);
    }

    var myChart = echarts.init($api.byId(id));
    var listdata = new Array();
    var  listlink=new Array();
    var locax=new Array(300,800,550,550,250,400,800,700);
    var locay=new Array(300,300,100,500,800,-150,100,200)
    var value1 =  {"list": [{"entity1": "广州数控", "rel": "型号", "entity2": "GSK980TD", "entity1_type": "品牌", "entity2_type": "型号"}, {"entity1": "GSK980TD", "rel": "故障代码", "entity2": "64", "entity1_type": "型号", "entity2_type": "故障代码"}, {"entity1": "64", "rel": "故障描述", "entity2": "G70~G73循环结束段使用了被禁止使用的 G指令 ", "entity1_type": "故障代码", "entity2_type": "故障描述"}, {"entity1": "G70~G73循环结束段使用了被禁止使用的 G指令 ", "rel": "故障类型", "entity2": "CNC报警", "entity1_type": "故障描述", "entity2_type": "故障类型"}, {"entity1": "G70~G73循环结束段使用了被禁止使用的 G指令 ", "rel": "解决方法", "entity2": "按复位键消除报警 , 再修改程序", "entity1_type": "故障描述", "entity2_type": "解决方法"}], "answer": ["按复位键消除报警 , 再修改程序"], "similar": ["97.62%"]}

      var obj1 = eval(value1).list;//json转化可用的
      var defin="";//用于存储节点
      var rnd=1,rnd2=2;
      var strtip="";
      var col="";
      for(var i =0;i<obj1.length;i++){
        pan1=defin.indexOf(obj1[i].entity1) != -1
        pan2=defin.indexOf(obj1[i].entity2) != -1

        if(pan1==false){//判断该节点名字是否已经存上了
          defin+=obj1[i].entity1
          if(obj1[i].entity1.length>9){
              strtip=obj1[i].entity1;
              obj1[i].entity1=obj1[i].entity1.substring(0,5)+"...";
            }
            if(obj1[i].entity1_type=="品牌")  col="#CC0000";
            if(obj1[i].entity1_type=="型号")  col="#CC66FF";
            if(obj1[i].entity1_type=="故障代码")  col="#99CCFF";
            if(obj1[i].entity1_type=="故障类型")  col="#97980e";
            if(obj1[i].entity1_type=="解决方法")  col="#888888";
            if(obj1[i].entity1_type=="故障描述")  col="#FA8072";
          tem={
              name: obj1[i].entity1,
              x: locax[i],
              y: locay[i],
              label: {
                 normal: {
                     show: true
                 }
             },
              itemStyle: {
                    normal: {
                        color:col,
                    }
                },
              tooltip:strtip
          };
          listdata.push(tem);
        }
        if(pan2==false){//判断该节点名字是否已经存上了
          defin+=obj1[i].entity2;
          if(obj1[i].entity2.length>9){
              strtip=obj1[i].entity2;
              obj1[i].entity2=obj1[i].entity2.substring(0,5)+"...";
            }
            if(obj1[i].entity2_type=="品牌")  col="#CC0000";
            if(obj1[i].entity2_type=="型号")  col="#CC66FF";
            if(obj1[i].entity2_type=="故障代码")  col="#99CCFF";
            if(obj1[i].entity2_type=="故障类型")  col="#97980e";
            if(obj1[i].entity2_type=="解决方法")  col="#888888";
            if(obj1[i].entity2_type=="故障描述")  col="#FA8072";
          tem1={
              name: obj1[i].entity2,
              x: locax[7-i],
              y: locay[7-i],
              label: {
                 normal: {
                     show: true
                 }
             },
              itemStyle: {
                    normal: {
                        color: col,
                    }
                },
              tooltip:strtip
          };
          listdata.push(tem1);
        }
      }
      for(var i =0;i<obj1.length;i++){
        if(obj1[i].entity1.length>9)
            obj1[i].entity1=obj1[i].entity1.substring(0,5)+"...";
        if(obj1[i].entity2.length>9)
            obj1[i].entity2=obj1[i].entity2.substring(0,5)+"...";
        tem4= {//两张写法
            source: obj1[i].entity1,
            target: obj1[i].entity2,
            label: {
                 normal: {
                     show: true,
                     formatter: obj1[i].rel
                 }
             },
            lineStyle: {
                normal: { curveness: 0.2 }
            }
        };
        listlink.push(tem4);
      }

    var app = {};
    option = null;

    option = {
      backgroundColor: '#eee',
    title: {
        text: '关系图谱'
    },
    tooltip: {},
    animationDurationUpdate: 550,
    animationEasingUpdate: 'quinticInOut',
    series : [
        {
            type: 'graph',
            layout: 'none',
            symbolSize: 50,
            roam: true,
            label: {
                normal: {
                    show: true
                }
            },
            edgeSymbol: ['circle', 'arrow'],
            edgeSymbolSize: [4, 10],
            edgeLabel: {
                normal: {
                    textStyle: {
                        fontSize: 10
                    }
                }
            },
            data: listdata,
            // links: [],
            links: listlink,
            lineStyle: {
                normal: {
                    opacity: 0.9,
                    width: 2,
                    curveness: 0
                }
            }
        }
    ]

};
    if (option && typeof option === "object") {
        myChart.setOption(option, true);
    }
}
