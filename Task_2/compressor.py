from PIL import Image
import numpy as np
from math import ceil

from Task_1.color_spaces import rgb_to_ycbcr, ycbcr_to_rgb
from Task_2.quality import adapt_table
from Task_1.Discret_Cos import dct_matrix_block, quntize, split_blocker, Q, idct_block, idct_matrix_block
from Task_2.write_in_file import save_compressed_image, load_image, decode_bitstream
from Task_2.zigzag import zic_zag_scan, inverse_zigzag
from Task_2.huffman import huff_encode_dc, huff_encode_ac, DC_HUFFMAN, AC_HUFFMAN
from Task_2.DC_RLE import ac_rle_encode, dc_encode, dc_decode

def bits_coder(blocks, Q_adapted, dc_codes, ac_codes):
    for block in blocks:
        coeff = dct_matrix_block(block)
        quant = quntize(coeff, Q_adapted)
        zigzag = zic_zag_scan(quant)
        dc_elem = zigzag[0]
        ac_elements = zigzag[1:]
        dc_codes.append(dc_elem)
        ac_rle_list = ac_rle_encode(ac_elements)
        for (runlength, value) in ac_rle_list:
            ac_bit_code = huff_encode_ac((runlength, value))
            ac_codes.append(ac_bit_code)

def compress_image(input_path, output_path, quality):
    Q = np.array([
        [16,11,10,16,24,40,51,61],
        [12,12,14,19,26,58,60,55],
        [14,13,16,24,40,57,69,56],
        [14,17,22,29,51,87,80,62],
        [18,22,37,56,68,109,103,77],
        [24,35,55,64,81,104,113,92],
        [49,64,78,87,103,121,120,101],
        [72,92,95,98,112,100,103,99]
    ])

    img = Image.open(input_path)
    if img.mode == "1":
        img = img.convert("L")
    arr = np.array(img)
    if img.mode == "L":
        mode = "grayscale"
    else:
        mode = "rgb"
    if mode == "rgb":
        arr = rgb_to_ycbcr(arr)
    Q_adapted = adapt_table(Q, quality)

    if mode=='grayscale':
        Y = arr
    else:
        Y = arr[:,:, 0]
        Cb = arr[:,:, 1]
        Cr = arr[:,:, 2]
    all_dc_codes = []
    all_ac_codes = []
    if mode == "rgb":
        YCbCr = [Y, Cb, Cr]
    else:
        YCbCr = [Y]
    for k in YCbCr:
        blocks_k = split_blocker(k)
        bits_coder(blocks_k, Q_adapted, all_dc_codes, all_ac_codes)
    dc_codes_encoded = dc_encode(all_dc_codes)
    dc_codes_bits = []
    for dc in dc_codes_encoded:
        dc_codes_bits.append(huff_encode_dc(dc))
    if mode == "grayscale":
        color_space = 0
    else:
        color_space = 1
    data = {
        'width': img.width,
        'height': img.height,
        'color_space': color_space,
        'quality': quality,
        'quant_table': Q_adapted,
        'dc_huffman_table': DC_HUFFMAN,
        'ac_huffman_table': AC_HUFFMAN,
        'dc_codes': dc_codes_bits,
        'ac_codes': all_ac_codes
    }
    save_compressed_image(output_path, data)


def reconstruct_component(dc_codes, ac_codes_list, blocks_per_row, blocks_per_col, quant_table):
    blocks = []
    for block_idx in range(len(dc_codes)):
        dc = dc_codes[block_idx]
        ac_pairs = ac_codes_list[block_idx]
        zigzag = [dc] + 63*[0]
        cur_pos = 1
        for (runlength, value) in ac_pairs:
            cur_pos+=runlength
            if cur_pos < 64:
                zigzag[cur_pos] = value
            cur_pos+=1
        matrix = inverse_zigzag(zigzag)
        matrix = matrix * quant_table
        block_pixel = idct_matrix_block(matrix)
        blocks.append(block_pixel)
    height = blocks_per_col * 8
    width = blocks_per_row * 8
    result = np.zeros((height, width), dtype=np.uint8)
    block_idx = 0
    for row_block in range(blocks_per_col):
        for col_block in range(blocks_per_row):
            y_start = row_block * 8
            x_start = col_block * 8
            result[y_start:y_start+8, x_start:x_start+8] = blocks[block_idx]
            block_idx += 1
    return result


def decompress_image(input_path, output_path):
    data = load_image(input_path)
    bitstream = data['bitstream']
    dc_huffman_table = data['dc_huffman_table']
    ac_huffman_table = data['ac_huffman_table']
    width = data['width']
    height = data['height']
    quant_table = data['quant_table']
    blocks_per_row = ceil(width / 8)
    blocks_per_col = ceil(height / 8)
    color_space = data['color_space']
    total_blocks_per_component = blocks_per_row * blocks_per_col
    if color_space == 1:
        expected_dc_count = total_blocks_per_component * 3  # Y, Cb, Cr
    else:
        expected_dc_count = total_blocks_per_component  # только Y
    dc_codes, ac_codes_list = decode_bitstream(bitstream, dc_huffman_table, ac_huffman_table, expected_dc_count)
    dc_codes = dc_decode(dc_codes)
    dc_per_component = total_blocks_per_component
    ac_per_component = total_blocks_per_component
    dc_codes_Y = dc_codes[0: dc_per_component]
    ac_codes_Y = ac_codes_list[0: ac_per_component]
    if color_space == 1:
        dc_codes_Cb = dc_codes[dc_per_component:2*dc_per_component]
        ac_codes_Cb = ac_codes_list[ac_per_component:2*ac_per_component]
        dc_codes_Cr = dc_codes[2*dc_per_component: 3*dc_per_component]
        ac_codes_Cr = ac_codes_list[2*ac_per_component: 3*ac_per_component]
        Y = reconstruct_component(dc_codes_Y, ac_codes_Y, blocks_per_row, blocks_per_col, quant_table)
        Cb = reconstruct_component(dc_codes_Cb, ac_codes_Cb, blocks_per_row, blocks_per_col, quant_table)
        Cr = reconstruct_component(dc_codes_Cr, ac_codes_Cr, blocks_per_row, blocks_per_col, quant_table)
        image_array = np.stack([Y, Cb, Cr], axis=2)
        image_array = ycbcr_to_rgb(image_array)
    else:
        Y = reconstruct_component(dc_codes_Y, ac_codes_Y, blocks_per_row, blocks_per_col, quant_table)
        image_array = Y
    image = Image.fromarray(image_array.astype(np.uint8))
    image.save(output_path)

def test():
    print("Тест 1")
    compress_image("../Task_1/lena.png", "test_lena.jpg", quality=50)
    print("Сжатие завершено")
    import os
    compressed_size = os.path.getsize("test_lena.jpg")
    print(f"Размер сжатого файла: {compressed_size} байт")
    print("\nТест 2: Распаковка test_lena.jpg...")
    decompress_image("test_lena.jpg", "test_lena_restored.png")
    print("Распаковка завершена")
    if os.path.exists("test_lena_restored.png"):
        restored_size = os.path.getsize("test_lena_restored.png")
        print(f"Восстановленное изображение создано: {restored_size} байт")
        print("ВСЕ ТЕСТЫ ПРОЙДЕНЫ")
    else:
        print("Восстановленный файл не создан")

if __name__ == "__main__":
    test()