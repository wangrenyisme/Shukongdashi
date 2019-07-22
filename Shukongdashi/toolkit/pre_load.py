# -*- coding: utf-8 -*-
import sys
import os
sys.path.append("..")

from Shukongdashi.Model.neo_models import Neo4j

from Shukongdashi.test_my.test_cnnrnn.predict import CnnModel
neo_con = Neo4j()   #预加载neo4j
neo_con.connectDB()
print('neo4j connected!')
cnn_model = CnnModel()
print('CnnModel loaded!')

# base_dir = os.getcwd()+'\\Shukongdashi\\demo\\data\\cnews'
# vocab_dir = os.path.join(base_dir, 'guzhang.vocab.txt')
#
# save_dir = os.getcwd()+'\\Shukongdashi\\demo\\checkpoints\\textcnn'
# save_path = os.path.join(save_dir, 'best_validation')  # 最佳验证结果保存路径
#
# person = Person(vocab_dir,save_path)
# print(person.Name)