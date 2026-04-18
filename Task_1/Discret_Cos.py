import numpy as np
from PIL import Image


def split_blocker(arr):
    blocks = []
    for y in range(0,arr.shape[0],8):
        for x in range(0,arr.shape[1],8):
            block = arr[y:y+8, x:x+8]
            blocks.append(block)
    return blocks

def alpha(k,N):
    if k==0:
        return np.sqrt(1/N)
    else:
        return np.sqrt(2/N)

def dct_block(block):
    N = 8
    block = block.astype(np.float32) - 128
    result = np.zeros((N,N), dtype=np.float32)
    for u in range(N):
        for v in range(N):
            s = 0
            for x in range(N):
                for y in range(N):
                    s+= block[x,y] * np.cos((2*x+1)*u*np.pi /(2*N)) * np.cos((2*y+1)*v*np.pi / (2*N))
            result[u,v] = alpha(u,N) * alpha(v,N) * s
    return result

def idct_block(coeffs):
    N = 8
    result = np.zeros((N,N), dtype=np.float32)
    for x in range(N):
        for y in range(N):
            s = 0
            for u in range(N):
                for v in range(N):
                    s+= coeffs[u,v]*alpha(u,N) * alpha(v,N)*np.cos((2*x+1)*u*np.pi /(2*N)) * np.cos((2*y+1)*v*np.pi / (2*N))
            result[x,y] = s + 128
    return result

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

def quntize(coeffs, Q):
    return np.round(coeffs/Q)

def dequntize(coeffs, Q):
    return coeffs*Q

def dct_matrix(N):
    D = np.zeros((N,N), dtype=np.float32)
    for u in range(N):
        for x in range(N):
            D[u,x] = alpha(u,N) * np.cos((2*x+1)*u*np.pi /(2*N))
    return D

def dct_matrix_block(block):
    D = dct_matrix(8)
    block = block.astype(np.float32) - 128
    return D @ block @ D.T

def idct_matrix_block(coeffs):
    D = dct_matrix(8)
    result = D.T @ coeffs @ D
    return result + 128

if __name__ == "__main__":
    lena = Image.open("lena.png")
    arr = np.array(lena)
    block = np.array(lena)[0:8, 0:8, 0].astype(np.float32)
    c1 = dct_block(block)
    c2 = dct_matrix_block(block)
    print("Максимальная разница DCT:", np.max(np.abs(c1 - c2)))