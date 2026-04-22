import sys
sys.path.insert(0, '..')
from Task_2.compressor import compress_image, decompress_image
import os

import sys
sys.path.insert(0, '..')

from Task_2.compressor import compress_image, decompress_image
import os
import json
import matplotlib.pyplot as plt

os.makedirs("results", exist_ok=True)
os.makedirs("graphs", exist_ok=True)

input_file = "/Users/emmat/PycharmProjects/AiSD_4sem_2Lab/Task_2/IMG_5729.JPG"


test_images = [("../Task_1/bw.jpg", "B&W No Dither", False)]
qualities = [10, 20, 30, 40, 50, 60, 70, 80, 90]
all_results = {}


for quality in [1, 2, 5, 10, 30]:
    compressed = f"my_test_q{quality}.jpg"
    restored = f"my_test_q{quality}_restored.png"
    compress_image(input_file, compressed, quality)
    decompress_image(compressed, restored)
    size_compressed = os.path.getsize(compressed)
    print(f"Quality {quality}: {size_compressed} байт")