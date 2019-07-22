from Shukongdashi.test_my.test_cnnrnn.predict import CnnModel

cnn_model = CnnModel()
test_demo = ['FANUC机床类型机床类型M的卧式加工中心',
             '伺服驱动主电源无法正常接通',
             '一台配套FANUC 0M的二手数控铣床，采用FANUC S系列主轴驱 动器',
             '开机后，不论输入S*! M03或S*! M04指令',
             '主轴仅仅出现低速旋转，实际转速无 法达到指令值。'

             ]
for i in test_demo:
    print(cnn_model.predict(i))
