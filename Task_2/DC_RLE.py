def dc_encode(dc_coeff):
    result = []
    result.append(dc_coeff[0])
    temp = dc_coeff[0]
    for i in range(2,len(dc_coeff)):
        x1 = dc_coeff[i-1]
        result.append(x1-temp)
        temp = x1
    result.append(dc_coeff[-1]-temp)
    return result

def dc_decode(diff_coeff):
    result = []
    result.append(diff_coeff[0])
    temp = diff_coeff[0]
    for i in range(2,len(diff_coeff)):
        x1 = diff_coeff[i-1]
        result.append(x1+temp)
        temp = x1+temp
    result.append(diff_coeff[-1]+temp)
    return result

def ac_rle_encode(ac_coeff):
    zero_count = 0
    result = []
    for coeff in ac_coeff:
        if coeff==0:
            zero_count+=1
        else:
            while zero_count >= 16:
                result.append((15, 0))
                zero_count -= 16
            result.append((zero_count,coeff))
            zero_count=0
    while zero_count >= 16:
        result.append((15,0))
        zero_count-=16
    result.append((0,0))
    return result


# dc = [100, 102, 98, 105, 110]
# encoded = dc_encode(dc)
# decoded = dc_decode(encoded)
# print(decoded ==dc)

# ac = [5, 0, 0, 3, 0, 7, 0, 0, 0, 0, 0, 0,0,0,0,0,0,0,0,0,0,0]
# ac_encoded = ac_rle_encode(ac)
# print(ac_encoded)

if __name__ == "__main__":
    dc = [100, 102, 98, 105, 110]
    encoded = dc_encode(dc)
    decoded = dc_decode(encoded)
    print(decoded ==dc)