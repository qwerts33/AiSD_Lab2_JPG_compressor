import sys
sys.path.insert(0, '..')
from Task_2.compressor import compress_image, decompress_image
import os

input_file = "/Users/emmat/PycharmProjects/AiSD_4sem_2Lab/Task_1/grayscale.jpg"

for quality in [50]:
    compressed = f"my_test_q{quality}.jpg"
    restored = f"my_test_q{quality}_restored.png"
    compress_image(input_file, compressed, quality)
    decompress_image(compressed, restored)
    size_compressed = os.path.getsize(compressed)
    print(f"Quality {quality}: {size_compressed} байт")