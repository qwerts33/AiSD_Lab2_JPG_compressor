import numpy as np
def zic_zag_scan(matrix):
    n = len(matrix)
    result = []
    for d in range(2*n-1):
        diagonal = []
        for i in range(n):
            j = d - i
            if 0 <= j < n:
                diagonal.append(matrix[i][j])
        if d%2==0:
            diagonal.reverse()
        result.extend(diagonal)
    return result

def zic_zag_scan_rectangular(matrix):
    n = len(matrix)
    m = len(matrix[0])
    result = []
    for d in range(n+m-1):
        diagonal = []
        for i in range(n):
            j = d - i
            if 0<=j < m:
                diagonal.append(matrix[i][j])
        if d%2==0:
            diagonal.reverse()
        result.extend(diagonal)
    return result

def inverse_zigzag(array):
    matrix = np.zeros((8, 8), dtype=np.float32)
    idx = 0
    for d in range(15):
        diagonal = []
        for i in range(8):
            j = d - i
            if 0 <= j < 8:
                diagonal.append((i, j))
        if d % 2 == 0:
            diagonal.reverse()
        for (i, j) in diagonal:
            matrix[i, j] = array[idx]
            idx += 1
    return matrix

test = np.array([[1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]])

rect = np.array([
    [1,  2,  3,  4,  5],
    [6,  7,  8,  9,  10],
    [11, 12, 13, 14, 15]
])

if __name__ == "__main__":
    print(zic_zag_scan_rectangular(rect))