import struct

def save_compressed_image(filename, data):
    with open(filename, 'wb') as f:
        f.write(b'JPG_')
        f.write(struct.pack('>I', data['width']))
        f.write(struct.pack('>I', data['height']))
        f.write(struct.pack('B', data['color_space']))
        f.write(struct.pack('B', data['quality']))
        table = data['quant_table']
        f.write(struct.pack("B", len(table)))
        for row in table:
            for elem in row:
                f.write(struct.pack("B", elem))
        dc_table = data['dc_huffman_table']
        f.write(struct.pack("B", len(dc_table)))
        for size, code in dc_table.items():
            f.write(struct.pack("B", size))
            f.write(struct.pack("B", len(code)))
            code_bytes = int(code, 2).to_bytes((len(code) + 7) // 8, byteorder='big')
            f.write(code_bytes)
        ac_table = data['ac_huffman_table']
        f.write(struct.pack('>H', len(ac_table)))
        for (runlength, size), code in ac_table.items():
            key_byte = (runlength<<4) | size
            f.write(struct.pack('B', key_byte))
            f.write(struct.pack('B', len(code)))
            code_bytes = int(code, 2).to_bytes((len(code) + 7) // 8, byteorder='big')
            f.write(code_bytes)
        bitstream = ''.join(data['dc_codes']) + ''.join(data['ac_codes'])
        padding = (8 - (len(bitstream) % 8)) % 8
        bitstream += '0' * padding
        f.write(struct.pack('B', padding))  # 1 байт (0-7)
        for i in range(0,len(bitstream), 8):
            byte_str = bitstream[i:i+8]
            byte_val = int(byte_str,2)
            f.write(struct.pack("B", byte_val))

def load_image(filename):
    with open(filename, 'rb') as f:
        signature = f.read(4)
        if signature != b'JPG_':
            raise ValueError("неправильный формат файла")
        width = struct.unpack('>I', f.read(4))[0]
        height = struct.unpack('>I', f.read(4))[0]
        color_space = struct.unpack('B', f.read(1))[0]
        quality = struct.unpack('B', f.read(1))[0]
        table_size = struct.unpack('B', f.read(1))[0]
        quant_table = []
        for y in range(table_size):
            row = []
            for x in range(table_size):
                elem = struct.unpack('B', f.read(1))[0]
                row.append(elem)
            quant_table.append(row)
        dc_table_count = struct.unpack('B', f.read(1))[0]
        dc_huffman_table = {}
        for _ in range(dc_table_count):
            size = struct.unpack('B', f.read(1))[0]
            code_len = struct.unpack('B', f.read(1))[0]
            code_bytes = f.read((code_len + 7) // 8)
            code_int = int.from_bytes(code_bytes, byteorder='big')
            code_str = format(code_int, f'0{code_len}b')
            dc_huffman_table[size] = code_str
        ac_table_count = struct.unpack('>H', f.read(2))[0]
        ac_huffman_table = {}
        for _ in range(ac_table_count):
            key_byte = struct.unpack('B', f.read(1))[0]
            runlength = key_byte >> 4
            size = key_byte & 0x0F
            code_len = struct.unpack('B', f.read(1))[0]
            code_bytes = f.read((code_len + 7) // 8)
            code_int = int.from_bytes(code_bytes, byteorder='big')
            code_str = format(code_int, f'0{code_len}b')
            ac_huffman_table[(runlength, size)] = code_str
        padding = struct.unpack('B', f.read(1))[0]
        remaining_bytes = f.read()
        bitstream = ''
        for byte_val in remaining_bytes:
            bitstream += format(byte_val, '08b')
        if padding > 0:
            bitstream = bitstream[:-padding]
        return {
            'width': width,
            'height': height,
            'color_space': color_space,
            'quality': quality,
            'quant_table': quant_table,
            'dc_huffman_table': dc_huffman_table,
            'ac_huffman_table': ac_huffman_table,
            'bitstream': bitstream
        }

def decode_vlc(vlc_bits, size):
    if size == 0:
        return 0
    vlc_value = int(vlc_bits, 2)
    if vlc_bits[0] == '0':
        return vlc_value - (2**size-1)
    else:
        return vlc_value

def decode_bitstream(bitstream, dc_huffman_table, ac_huffman_table, expected_dc_count):
    dc_reverse = {}
    for size, code in dc_huffman_table.items():
        dc_reverse[code] = size
    ac_reverse = {}
    for (runlength, size), code in ac_huffman_table.items():
        ac_reverse[code] = (runlength, size)
    i = 0
    dc_codes = []
    n = len(bitstream)
    while len(dc_codes) < expected_dc_count:
        dc_found = False
        for length in range(2,14):
            code_fragment = bitstream[i:i+length]
            if code_fragment in dc_reverse:
                size = dc_reverse[code_fragment]
                vlc_bits = bitstream[i+length: i+length+size]
                dc_value = decode_vlc(vlc_bits, size)
                dc_codes.append(dc_value)
                i+=length+size
                dc_found = True
                break
        if not dc_found:
            print(f"ERROR at pos {i}, read {len(dc_codes)} DC codes so far")
            print(f"Fragment: {bitstream[i:i+20]}")
            raise ValueError("Ошибка парсинга DC")
    ac_codes_list = []
    current_ac_block = []
    while True:
        if len(ac_codes_list) >= expected_dc_count:
            break
        ac_found = False
        for length in range(2, 15):
            code_fragment = bitstream[i:i+length]
            if code_fragment in ac_reverse:
                (runlength, size) = ac_reverse[code_fragment]
                if runlength == 0 and size == 0:  # EOB
                    i += length
                    ac_codes_list.append(current_ac_block)
                    current_ac_block = []
                    ac_found = True
                    break
                vlc_bits = bitstream[i+length: i+length+size]
                ac_value = decode_vlc(vlc_bits, size)
                current_ac_block.append((runlength, ac_value))
                i += length + size
                ac_found = True
                break
        if not ac_found:
            print(f"Ошибка парсинга AC на позиции {i}")
            print(f"Прочитано DC: {len(dc_codes)}")
            print(f"Прочитано AC блоков: {len(ac_codes_list)}")
            print(f"Текущий AC блок: {len(current_ac_block)} пар")
            print(f"Пробуем коды: {bitstream[i:i+20]}")
            print(f"Доступные AC коды (первые 5): {list(ac_reverse.keys())[:5]}")
            print(f"DEBUG: i={i}, len(bitstream)={len(bitstream)}, осталось={len(bitstream)-i}")
            raise ValueError("Ошибка парсинга AC")
    
    return dc_codes, ac_codes_list