import cv2 as cv
import sys


file_name = 'ultra_light.jpg'
img_raw = cv.imread(file_name)

if img_raw is None:
    print(f"오류: '{file_name}' 파일을 찾을 수 없습니다. 프로그램을 종료합니다.")
    sys.exit()

screen_width = 800
ratio = screen_width / float(img_raw.shape[1])
dim = (screen_width, int(img_raw.shape[0] * ratio))
img = cv.resize(img_raw, dim, interpolation=cv.INTER_AREA)


shape_info = img.shape
h = shape_info[0]
w = shape_info[1]
c = shape_info[2] if len(shape_info) == 3 else 1

print(f"--- 영상 정보 (화면 맞춤 후) ---")
print(f"데이터 타입: {img.dtype}")
print(f"영상 형태: 가로({w}), 세로({h}), 채널({c})")


gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
resized_img = cv.resize(gray_img, (0, 0), fx=0.5, fy=0.5, interpolation=cv.INTER_AREA)

cv.rectangle(resized_img, (10, 10), (220, 55), 255, 2)
cv.putText(resized_img, "2026.03.20", (20, 43), 
            cv.FONT_HERSHEY_SIMPLEX, 0.8, 255, 2)


cv.rectangle(img, (10, 10), (220, 55), 255, 2)
cv.putText(img, "2026.03.20", (20, 43), 
            cv.FONT_HERSHEY_SIMPLEX, 0.8, 255, 2)

cv.namedWindow('Original Color', cv.WINDOW_AUTOSIZE)
cv.namedWindow('Processed Gray', cv.WINDOW_AUTOSIZE)
cv.imshow('Original Color', img)        
cv.imshow('Processed Gray', resized_img) 
cv.waitKey(1)
cv.waitKey(0)
cv.destroyAllWindows()