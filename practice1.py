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

#2부터 시작하는 구구단
A = int(input("2-9숫자" ))
if 1< A <10:
    B = 1
    while True:
        if B<10:
            C=A*B
            print(A,"*",B,"=",C)
            B +=1
        else:
            break
print("끝")

#위에 코드 단순화
A = int(input("2-9숫자: "))

if 1 < A < 10:
    for B in range(1, 10):  # B를 1부터 9까지 자동으로 반복!
        print(A, "*", B, "=", A * B)

print("끝")

A = int(input("2-9숫자: "))

#더하기로 구구단 만들기
if 1 < A < 10:
    for B in range(1, 10):
        # 곱셈 결과(C)를 0으로 초기화
        C = 0
        
        # A를 B번 더하는 과정
        for _ in range(B):
            C += A
            
        print(A, "*", B, "=", C)

print("끝")
#3일차 수업 끝
#3일차 정처기 Class, self
class ClassicCar:
    color = "빨간색"

    def test(self):
        color = "파란색"
        print("color = ", color)
        print("self.color = ", self.color)

father = ClassicCar()
father.test()
father.color = "검은색"
father.test()