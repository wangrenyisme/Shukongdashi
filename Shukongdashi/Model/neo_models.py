from py2neo import Graph, Node, Relationship, cypher, Path
class Neo4j():
	graph = None
	def __init__(self):
		print("create neo4j class ...")

	def connectDB(self):
		self.graph = Graph("http://localhost:7474", username="neo4j", password="hadoop")
	#下面两个函数分别是插入节点和关系
	def insertNode(self,entity,lable):
		try:
			self.graph.run("CREATE (c:" + str(lable) + "{ title: \"" + str(entity) + "\"})")
		except:
			print('已经存在节点')
		return
	def insertRelation(self,entity1,relation, entity2,lable1,lable2):
		answer = self.graph.run("MATCH (n1 {title:\""+str(entity1)+"\"})- [rel{type:\""+str(relation)+"\"}] -> (n2 {title:\""+str(entity2)+"\"}) RETURN n1,rel,n2" ).data()
		if len(answer) ==0:
			print("创建关联")
			self.graph.run("MATCH (a:" + str(lable1) + "),(b:" + str(lable2) + ") WHERE a.title = \"" + str(entity1) + "\" AND b.title = \"" + str(entity2) + "\" CREATE (a)-[r:"+str(lable1[0]+lable2[0])+"{ type:\"" + str(relation) + "\" }]->(b)")
		else:
			print("已存在关联")
		return

	def findNode(self,title):
		sql = "MATCH (n {title: '" + str(title) + "' }) return n;"
		answer = self.graph.run(sql).data()
		return answer


	def matchItembyTitle(self,value):
		sql = "MATCH (n:Item { title: '" + str(value) + "' }) return n;"
		answer = self.graph.run(sql).data()
		return answer
	#模糊查询相似的故障
	def findBuquanItems(self,question_start):
		sql = "match (n:Describe) where n.title =~'.*"+question_start+".*' return n"
		answer = self.graph.run(sql).data()
		return answer
	# 根据title值返回互动百科item
	def matchHudongItembyTitle(self,value):
		sql = "MATCH (n:HudongItem { title: '" + str(value) + "' }) return n;"
		answer = self.graph.run(sql).data()
		return answer

	# 根据entity的名称返回关系
	def getEntityRelationbyEntity(self,value):
		answer = self.graph.run("MATCH (entity1) - [rel] -> (entity2)  WHERE entity1.title = \"" +str(value)+"\" RETURN rel,entity2").data()
		return answer

	#查找entity1及其对应的关系（与getEntityRelationbyEntity的差别就是返回值不一样）
	def findRelationByEntity(self,entity1):
		answer = self.graph.run("MATCH (n1 {title:\""+str(entity1)+"\"})- [rel] -> (n2) RETURN n1,rel,n2" ).data()
		# if(answer is None):
		# 	answer = self.graph.run("MATCH (n1:NewNode {title:\""+entity1+"\"})- [rel] -> (n2) RETURN n1,rel,n2" ).data()
		return answer

	#查找entity2及其对应的关系
	def findRelationByEntity2(self,entity1):
		answer = self.graph.run("MATCH (n1)- [rel] -> (n2 {title:\""+str(entity1)+"\"}) RETURN n1,rel,n2" ).data()

		# if(answer is None):
		# 	answer = self.graph.run("MATCH (n1)- [rel] -> (n2:NewNode {title:\""+entity1+"\"}) RETURN n1,rel,n2" ).data()
		return answer

	#根据entity1和关系查找enitty2
	def findOtherEntities(self,entity,relation):
		answer = self.graph.run("MATCH (n1 {title:\"" + str(entity) + "\"})- [rel {type:\""+str(relation)+"\"}] -> (n2) RETURN n1,rel,n2" ).data()
		#if(answer is None):
		#	answer = self.graph.run("MATCH (n1:NewNode {title:\"" + entity + "\"})- [rel:RELATION {type:\""+relation+"\"}] -> (n2) RETURN n1,rel,n2" ).data()

		return answer
	def findAllDescribes(self):
		answer = self.graph.run("match (m:Describe) return m").data()
		return answer
	#根据类别查找所有的节点
	def findEntitiesByType(self,type):
		answer = self.graph.run("match (m:"+str(type)+") return m").data()
		return answer
	#根据entity2和关系查找enitty1
	def findOtherEntities2(self,entity,relation):
		answer = self.graph.run("MATCH (n1)- [rel {type:\""+str(relation)+"\"}] -> (n2 {title:\"" + str(entity) + "\"}) RETURN n1,rel,n2" ).data()
		#if(answer is None):
		#	answer = self.graph.run("MATCH (n1)- [rel:RELATION {type:\""+relation+"\"}] -> (n2:NewNode {title:\"" + entity + "\"}) RETURN n1,rel,n2" ).data()

		return answer
	#根据entity2和关系查找enitty1的个数
	def findNumberOfEntities1(self,entity,relation):
		answer = self.graph.run("MATCH  (n)-[r {type:\""+str(relation)+"\"}]->(m {title:\"" + str(entity) + "\"}) WITH count(n) as relathionCount RETURN relathionCount").data()
		return answer