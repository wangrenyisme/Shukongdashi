
from __future__ import print_function


import tensorflow as tf
import tensorflow.contrib.keras as kr
import os
from Shukongdashi.test_my.test_cnnrnn.cnn_model import TCNNConfig, TextCNN
from Shukongdashi.test_my.test_cnnrnn.data.cnews_loader import read_category, read_vocab
try:
    bool(type(unicode))
except NameError:
    unicode = str


class Person:
    # constructor
    def __init__(self,vocab_dir,save_path):
        self.Name = vocab_dir
        self.Sex = save_path
        # self.config = TCNNConfig()
        # self.categories, self.cat_to_id = read_category()
        # self.words, self.word_to_id = read_vocab(vocab_dir)
        # self.config.vocab_size = len(self.words)
        # self.model = TextCNN(self.config)
        #
        # self.session = tf.Session()
        # self.session.run(tf.global_variables_initializer())
        # saver = tf.train.Saver()
        # saver.restore(sess=self.session, save_path=save_path)  # 读取保存的模型

    def ToString(self):
        return 'Name:' + self.Name + ',Sex:' + self.Sex