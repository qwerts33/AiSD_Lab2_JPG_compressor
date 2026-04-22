import os.path

from PIL import Image
import numpy as np

def save_raw(image, filename, img_type):
    arr = np.array(image)
    width = image.size[0]
    height = image.size[1]
    with open(filename, "wb") as file:
        file.write(img_type.to_bytes(1, byteorder="big"))
        file.write(width.to_bytes(2, byteorder="big"))
        file.write(height.to_bytes(2, byteorder="big"))
        file.write(arr.tobytes())

def load_raw(filename):
    with open(filename, "rb") as file:
        img_type = int.from_bytes(file.read(1), byteorder="big")
        width = int.from_bytes(file.read(2), byteorder="big")
        height = int.from_bytes(file.read(2), byteorder="big")
        arr = file.read()
        arr = np.frombuffer(arr, dtype=np.uint8)
        if img_type == 1:
            arr = arr.reshape(height, width,3)
        else:
            arr = arr.reshape(height, width)
    return img_type, arr

if __name__ == "__main__":
    img = Image.open("rgb.png")

    img_grayscale = img.convert("L")
    img_bw = img_grayscale.convert(mode='1', dither=Image.Dither.NONE)

    img_grayscale.save("grayscale.png")
    img_bw.save("bw.png")

    img_bw_wd = img_grayscale.convert(mode='1')
    img_bw_wd.save("bw_wd.png")

    lena = Image.open("lena.png")
    save_raw(lena, "lena.raw", 1)
    save_raw(img, "rgb.raw", 1)
    save_raw(img_grayscale, "grayscale.raw", 0)
    save_raw(img_bw, "bw.raw", 2)
    save_raw(img_bw_wd, "bw_wd.raw", 2)

    print("Сравнение")
    lena_png_size = os.path.getsize("lena.png")
    lena_raw_size = os.path.getsize("lena.raw")
    print(f"Lena.png RGB: {lena_png_size} байт - {lena_raw_size} байт, коэф: {lena_raw_size/lena_png_size:.2f}")
    rgb_png_size = os.path.getsize("rgb.png")
    rgb_raw_size = os.path.getsize("rgb.raw")
    print(f"RGB: {rgb_png_size} байт - {rgb_raw_size} байт, коэф: {rgb_raw_size/rgb_png_size:.2f}")
    grayscale_png_size = os.path.getsize("grayscale.jpg")
    grayscale_raw_size = os.path.getsize("grayscale.raw")
    print(f"GrayScale: {grayscale_png_size} байт - {grayscale_raw_size} байт, коэф: {grayscale_raw_size/grayscale_png_size:.2f}")
    bw_png_size = os.path.getsize("bw.jpg")
    bw_raw_size = os.path.getsize("bw.raw")
    print(f"BW: {bw_png_size} байт - {bw_raw_size} байт, коэф: {bw_raw_size/bw_png_size:.2f}")
    bw_wd_png_size = os.path.getsize("bw_wd.jpg")
    bw_wd_raw_size = os.path.getsize("bw_wd.raw")
    print(f"BW_wd: {bw_wd_png_size} байт - {bw_wd_raw_size} байт, коэф: {bw_wd_raw_size/bw_wd_png_size:.2f}")
