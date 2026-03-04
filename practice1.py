s = "Hello Python"
print (s[-2:])
print(s[2:])

a = [1,2,3,4,5]
a[0:4:2] = ['a', 'b']
print(a)

d = {"name" : "파이썬", "age" : 20}
d["sight"] = 1.5
d["age"] = 30
print(d)

a = [10, 20, 30]
for i in a:
    print(i, end=" ")
# print() 함수는 원래 한번 출력하고 자동으로 줄을 바꿈 하지만
# end=" "를 넣어주면 줄바꿈 대신 한칸 띄어쓰기로 끝내달라는 뜻
#end= " " : 10 20 30
#end= "" : 102030
#end="\n" : 10
            #20
            #30

#while
sum = 0
cnt = 1
while True:
    sum += cnt
    if sum > 100:
        break
    cnt += 1
print(cnt)

#함수정의
def multi(num):
    num*=2
    return num

a = int(input("20:"))
res = multi(a)
print(res)
