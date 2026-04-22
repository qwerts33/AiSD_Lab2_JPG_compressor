from math import ceil
def adapt_table(original_table, quality):
    if 1 <= quality < 50:
        S = 5000 / quality
    elif 50 <= quality <= 100:
        S = 200 - 2 * quality
    new_table = [[0 for _ in range(len(original_table[0]))] for _ in range(len(original_table))]
    for y in range(len(original_table)):
        for x in range(len(original_table[y])):
            q = (original_table[y][x] * S) / 100
            q = ceil(q)
            if q<1:
                new_table[y][x]=1
            else:
                new_table[y][x] = min(q, 255)
    return new_table