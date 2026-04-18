def get_category(x):
    if x==0:
        return 0
    else:
        return abs(int(x)).bit_length()

def get_vlc_code(x):
    if x>0:
        return x
    else:
        return x + 2 **get_category(x) - 1

if __name__ == "__main__":
    print(get_category(5))   # 3
    print(get_vlc_code(5))   # 5
    print(get_category(-5))  # 3
    print(get_vlc_code(-5))  # -5 + 8 - 1 = 2