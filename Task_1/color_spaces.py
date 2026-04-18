import numpy as np
from PIL import Image

def rgb_to_ycbcr(arr):
    arr_ycbcr = []
    for row in arr:
        for pixel in row:
            R,G,B = pixel
            Y = 0.299*R + 0.587*G + 0.114*B
            Cb = -0.169*R - 0.331*G + 0.5*B + 128
            Cr = 0.5*R - 0.419*G - 0.081*B + 128
            arr_ycbcr.append([Y,Cb,Cr])
    arr_ycbcr = np.array(arr_ycbcr, dtype=np.float32)
    arr_ycbcr = np.clip(arr_ycbcr, 0, 255)
    arr_ycbcr = arr_ycbcr.reshape(arr.shape[0], arr.shape[1], 3)
    return arr_ycbcr.astype(np.uint8)


#print(len(result), result[0])

def ycbcr_to_rgb(arr):
    arr = arr.astype(np.float32)
    arr_rgb = []
    for row in arr:
        for pixel in row:
            Y,Cb,Cr = pixel
            R = Y + 1.402*(Cr - 128)
            G = Y - 0.344*(Cb - 128) - 0.714*(Cr - 128)
            B = Y + 1.772*(Cb - 128)
            arr_rgb.append([R,G,B])
    arr_rgb = np.array(arr_rgb, dtype=np.float32)
    arr_rgb = np.clip(arr_rgb, 0, 255)
    arr_rgb = arr_rgb.reshape(arr.shape[0], arr.shape[1], 3)
    return arr_rgb.astype(np.uint8)

if __name__ == "__main__":
    arr = np.array(Image.open("lena.png")).astype(np.float32)
    result = rgb_to_ycbcr(arr)
    lena = Image.open("lena.png")
    lena.show()
    lena_2 = rgb_to_ycbcr(np.array(lena).astype(np.float32))
    Image.fromarray(lena_2, mode="YCbCr").show()
    lena_1 = ycbcr_to_rgb(lena_2)
    Image.fromarray(lena_1).show()

    arr = np.array(lena)
    print(f"Оригинал: {arr[0][0]}")
    print(f"Восстановленный: {lena_1[0][0]}")
    print(f"Макс. Разница: {np.max(np.abs(arr.astype(np.int16) - lena_1.astype(np.int16)))}")