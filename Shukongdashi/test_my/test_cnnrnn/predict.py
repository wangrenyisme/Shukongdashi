# coding: utf-8

from __future__ import print_function

import os
import tensorflow as tf
import tensorflow.contrib.keras as kr

from Shukongdashi.test_my.test_cnnrnn.cnn_model import TCNNConfig, TextCNN
from Shukongdashi.test_my.test_cnnrnn.data.cnews_loader import read_category, read_vocab

try:
    bool(type(unicode))
except NameError:
    unicode = str

base_dir = os.getcwd()+'\\Shukongdashi\\demo\\data\\cnews'
vocab_dir = os.path.join(base_dir, 'guzhang.vocab.txt')

save_dir = os.getcwd()+'\\Shukongdashi\\demo\\checkpoints\\textcnn'
save_path = os.path.join(save_dir, 'best_validation')  # 最佳验证结果保存路径


class CnnModel:
    def __init__(self):
        self.config = TCNNConfig()
        self.categories, self.cat_to_id = read_category()
        self.words, self.word_to_id = read_vocab(vocab_dir)
        self.config.vocab_size = len(self.words)
        self.model = TextCNN(self.config)

        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        saver.restore(sess=self.session, save_path=save_path)  # 读取保存的模型

    def predict(self, message):
        # 支持不论在python2还是python3下训练的模型都可以在2或者3的环境下运行
        content = unicode(message)
        data = [self.word_to_id[x] for x in content if x in self.word_to_id]

        feed_dict = {
            self.model.input_x: kr.preprocessing.sequence.pad_sequences([data], self.config.seq_length),
            self.model.keep_prob: 1.0
        }

        y_pred_cls = self.session.run(self.model.y_pred_cls, feed_dict=feed_dict)
        return self.categories[y_pred_cls[0]]


if __name__ == '__main__':
    cnn_model = CnnModel()
    test_demo = ['FANUC机床类型机床类型M的卧式加工中心',
                 '伺服驱动主电源无法正常接通',
                 '一台配套FANUC 0M的二手数控铣床，采用FANUC S系列主轴驱 动器',
                 '开机后，不论输入S*! M03或S*! M04指令',
                 '主轴仅仅出现低速旋转，实际转速无 法达到指令值。'

                 ]
    for i in test_demo:
        print(cnn_model.predict(i))
