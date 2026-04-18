import numpy as np
from PIL import Image

def downsampling(arr):
    new_arr = arr[::2,::2]
    return new_arr

def upsampling(arr):
    arr = np.repeat(arr, 2, axis=0)
    arr = np.repeat(arr, 2, axis=1)
    return arr

def lerp(x1,x2,y1,y2,x):
    if x1==x2:
        return y1
    y = y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return y

def spline(xs, ys, x):
    for i in range(len(xs)-1):
        if xs[i] <= x <= xs[i+1]:
            return lerp(xs[i], xs[i+1], ys[i], ys[i+1], x)

def bilinear(x1,x2,y1,y2,z11,z12,z21,z22,x,y):
    a = lerp(x1,x2,z11,z21,x)
    b = lerp(x1,x2,z12,z22,x)
    return lerp(y1,y2,a,b,y)

def upsample_bilinear(arr):
    arr = arr.astype(np.float32)
    height, width = arr.shape[:2]
    new_height, new_width = height*2, width*2
    result = np.zeros((new_height, new_width, 3), dtype=np.float32)
    for y in range(new_height):
        for x in range(new_width):
            if x%2 == 0 and y%2 == 0:
                result[y,x] = arr[y//2,x//2]
            elif x%2!=0 and y%2==0:
                left = arr[y//2,x//2]
                right = arr[y//2,min(x//2+1, width-1)]
                inter = lerp(x//2,x//2+1,left,right,x/2)
                result[y,x] = inter
            elif x%2==0 and y%2!=0:
                top = arr[y//2,x//2]
                bottom = arr[min(y//2+1,height-1),x//2]
                inter = lerp(y//2,y//2+1,top,bottom,y/2)
                result[y,x] = inter
            else:
                top_left = arr[y//2,x//2]
                top_right = arr[y//2,min(x//2+1, width-1)]
                bottom_left = arr[min(y//2+1,height-1),x//2]
                bottom_right = arr[min(y//2+1,height-1),min(x//2+1,width-1)]
                inter = bilinear(x//2,x//2+1,y//2,y//2+1,top_left,top_right,bottom_left,bottom_right,x/2,y/2)
                result[y,x] = inter
    result = np.clip(result,0,255)
    return result.astype(np.uint8)

def resize(arr,new_height, new_width):
    arr = arr.astype(np.float32)
    old_height, old_width = arr.shape[:2]
    result = np.zeros((new_height,new_width,3),dtype=np.float32)
    for y in range(new_height):
        for x in range(new_width):
            old_x = x * (old_width-1)/(new_width-1)
            old_y = y *(old_height-1)/(new_height-1)
            x1 = int(old_x)
            x2 = min(x1+1, old_width-1)
            y1 = int(old_y)
            y2 = min(y1+1, old_height-1)
            z11 = arr[y1,x1]
            z12 = arr[y1,x2]
            z21 = arr[y2,x1]
            z22 = arr[y2,x2]
            bil = bilinear(x1,x2,y1,y2,z11,z12,z21,z22,old_x,old_y)
            result[y,x] = bil
    result = np.clip(result, 0, 255)
    return result.astype(np.uint8)


lena = Image.open("lena.png")
arr = np.array(lena)
arr_after_down = downsampling(arr)
arr_back = upsampling(arr_after_down)
#print(spline([0, 2, 5, 10], [0, 4, 1, 8], 3))  # между x=2 и x=5
#print(spline([0, 2, 5, 10], [0, 4, 1, 8], 7))  # между x=5 и x=10
#print(bilinear(0, 2, 0, 2, 0, 0, 0, 4, 1, 1))  # должно дать 1.0

arr_back_new = upsample_bilinear(arr_after_down)
#lena.show()
#Image.fromarray(arr_back).show()
#Image.fromarray(arr_back_new).show()
'''
#print("Оригинал [0,0]:", arr[0,0])
#print("После down+up [0,0]:", arr_back_new[0,0])
#print("Оригинал [0,1]:", arr[0,1])
#print("После down+up [0,1]:", arr_back_new[0,1])
width = arr_after_down.shape[1]
y, x = 0, 1
left = arr_after_down[y//2, x//2]
right = arr_after_down[y//2, min(x//2+1, width-1)]
print("left:", left)
print("right:", right)
print("lerp result:", lerp(x//2, x//2+1, left, right, x/2))'''