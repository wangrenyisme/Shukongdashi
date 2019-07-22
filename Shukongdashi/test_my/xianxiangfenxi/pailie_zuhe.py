import re
l = [1, 2, 3]
from itertools import combinations
zuhe_xianxiaing = list(combinations(l, 2))
for zuhe in zuhe_xianxiaing:
    print(zuhe[0],zuhe[1])
    print(zuhe[1],zuhe[0])
miaoshu = 'A,B，C'
erroridlist = re.split(',|，', miaoshu)
print(erroridlist)