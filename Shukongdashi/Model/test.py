s='hello'
t=" world"
s=s+t
print(s,s[-1],s[2:8])
print(str(10 + 5//3 -True+False))
print(round(17.0/3**2,2))
print( 0 and 1 or not 2<True)
print(int("20", 16), int("101",2))

def printYanghui(n):
    N = [1]
    for i in range(n):
        L = N.copy()  # 我们需要吧N复制给L,而不能直接L = N，因为这样L和N会在同一个地址，后续算法就会出错
        for j in range(len(L)):  # 遍历和转化
            temp = str(L[j])
            L[j] = temp
        l = ' '.join(L).center(2*n-1)  #组合和剧中一起写
        print(l)      #这里就是打印l了
        N.append(0)   #因为复制之后L是L，N是N，所以我们还是继续在N末尾加0
        N = [N[k] + N[k-1] for k in range(i+2)]
    return

printYanghui(5)

def temp(j,i):
    m=1
    n=1
    for t in range(j,0,-1):
        m*=t
    for k in range(i-j+1,i+1):
        n*=k
    return n/m
def printYanghui(n):
        for i in range(n,0,-1):
            for j in range(i-1,0,-1):
                print(" ", end='')
            for k in range(0,n-i+1):
                if k==0:
                    print("1 ", end='')
                    continue
                if k==n-i:
                    print("1 ", end='')
                    continue
                else:
                    print("%d"%(temp(k,n-i)), end=' ')
            print()


x=eval(input())
y=[]
for i in range(0,len(x)):
  if x[i] not in y:
    y.append(x[i])
for j in range(0,len(y)-1):
  print('%d'%y[j],end=' ')
print(y[-1])