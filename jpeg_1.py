# -*- coding: utf-8 -*-
"""JPEG_1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1adImMElZcW4qX6IAbGI56IT_aocYXCbX

# **In this version, I have implemented the original huffman coding algorithm**

READ THE IMAGE
"""

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd 
import math
import cv2
from matplotlib import pyplot as plt
import matplotlib.pylab as pylab

# %pprint
# %matplotlib inline
pylab.rcParams['figure.figsize'] = (20.0, 7.0)

img = cv2.imread('/content/MARBLES.BMP',cv2.IMREAD_GRAYSCALE)

plt.figure(figsize=(10,10))
plt.imshow(img,cmap='gray')

height = img.shape[0]
width = img.shape[1]

print('height=',height )
print('width=',width )

height = int(math.ceil(height/8)*8)
width  = int(math.ceil(width/8)*8)

print('height=',height )
print('width=',width )

img = cv2.resize(img,(width,height,))
img.shape

plt.figure(figsize=(10,10))
plt.imshow(img,cmap='gray')

"""FUNCTION FOR DCT"""

def dct2(a):
    return scipy.fftpack.dct( scipy.fftpack.dct( a, axis=0, norm='ortho' ), axis=1, norm='ortho' )

def idct2(a):
    return scipy.fftpack.idct( scipy.fftpack.idct( a, axis=0 , norm='ortho'), axis=1 , norm='ortho')

"""PERFORM DCT"""

import numpy as np
import matplotlib.pyplot as plt
import scipy

from numpy import pi
from numpy import sin
from numpy import zeros
from numpy import r_
from scipy import signal
from scipy import misc # pip install Pillow
import matplotlib.pylab as pylab

imsize = img.shape
dct = np.zeros(imsize)

# Do 8x8 DCT on image (in-place)
for i in r_[:imsize[0]:8]:
    for j in r_[:imsize[1]:8]:
        dct[i:(i+8),j:(j+8)] = dct2( img[i:(i+8),j:(j+8)] )

pos = 128
# Extract a block from image
plt.figure()
plt.imshow(img[pos:pos+8,pos:pos+8],cmap='gray')
plt.title( "An 8x8 Image block")

# Display the dct of that block
plt.figure()
plt.imshow(dct[pos:pos+8,pos:pos+8],cmap='gray',vmax= np.max(dct)*0.01,vmin = 0, extent=[0,pi,pi,0])
plt.title( "An 8x8 DCT block")

plt.figure()
plt.imshow(dct,cmap='gray',vmax = np.max(dct)*0.01,vmin = 0)
plt.title( "8x8 DCTs of the image")

"""QUANTIZATION MATRIX"""

def QMatrix(q):
  Q = np.array([[16,11,10,16,24,40,51,61],
              [12,12,14,19,26,58,60,55],
              [14,13,16,24,40,57,69,56],
              [14,17,22,29,51,87,80,62],
              [18,22,37,56,68,109,103,77],
              [24,35,55,64,81,104,113,92],
              [49,64,78,87,103,121,120,101],
              [72,92,95,98,112,100,130,99]])
  Q_new = np.empty([8,8])

  if q<50:
    S = 5000/q
  else:
    S = 200 - 2*q

  for i in range(8):
    for j in range(8):
      Q_new[i][j] = math.floor((S*Q[i][j]+50)/100)
      if Q_new[i][j] > 255:
        Q_new[i][j] = 255

  return Q_new

quality = int(input('CHOOSE QUALITY FROM 10,50, AND 90'))
Q = QMatrix(quality)

temp = np.concatenate((Q,Q))
for i in range((height//8)-2):
  temp = np.concatenate((temp,Q))
temp_2 = np.concatenate((temp,temp),axis=1)
for i in range((width//8)-2):
  temp_2 = np.concatenate((temp_2,temp),axis=1)
Q = temp_2

Q.shape

quantized = np.round(np.divide(dct,Q))

plt.figure()
plt.imshow(quantized,cmap='gray',vmax = np.max(quantized)*0.01,vmin = 0)
plt.title( "QUANTIZED image")

"""SLICING THE ARRAY"""

sliced = np.empty([height,width])

def blockshaped(arr, nrows, ncols):
    h, w = arr.shape
    assert h % nrows == 0
    assert w % ncols == 0 
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1,2)
               .reshape(-1, nrows, ncols))

sliced = blockshaped(quantized,int(height/126),int(width/178))
sliced = sliced.reshape(126,178,8,8).astype(int)
sliced[10][45]

"""ZIG ZAG SCANNING"""

def zigzagger(matrix):
  rows = 8
  columns = 8
  solution=[[] for i in range(rows+columns-1)] 
  
  for i in range(rows): 
      for j in range(columns): 
          sum=i+j 
          if(sum%2 ==0):    
              solution[sum].insert(0,matrix[i][j]) 
          else:     
              solution[sum].append(matrix[i][j]) 
            
  final = list()           
  for i in solution: 
      for j in i: 
          final.append(j)
  return final

vector = list()

for i in range(126):
  for j in range(178):
    a = zigzagger(sliced[i][j])
    vector.append(a)
vector = np.asarray(vector)

"""DPCM"""

def DPCM(data):
  l = len(data)
  for i in range(l-1,0,-1):
    data[i][0] = data[i][0] - data[i-1][0]
  return data

vector = DPCM(vector)

DC_c = list() #DC components
for i in range(len(vector)):
  DC_c.append(vector[i][0])

"""RLE on AC Components"""

from itertools import chain, groupby

def RLE_AC(iterable):
  final = list()
  x =  list(chain.from_iterable((len([*thing]),val) for val, thing in groupby(iterable)))
  for i in range(0,len(x),2):
    if x[i+1] != 0:
      final.extend([x[i+1]]*x[i])
    else:
      final.append(x[i])
      final.append(0)
  return np.asarray(final)

n_coded = list()
for i in range(len(vector)):
  n_coded.append(RLE_AC(vector[i]))

# temp_d = list()
# for i in range(len(n_coded)):
#   for j in range(0,len(n_coded[i])):
#     temp_d.append(str(n_coded[i][j]))

"""HUFFMAN on DC"""

bitstream = list()

size_codes = dict({0:'00',1:'010',2:'011',3:'100',4:'101',5:'110',6:'1110',7:'11110',8:'111110',9:'1111110',10:'11111110',11:'111111110'})

def tostr(s): 
    new = "" 
    for x in s: 
        new += x   
    return new 

def DC_HUFF(num):
  global value
  if num >= 0:
    value = bin(num)[2:]
  elif num < 0:
    value = list(bin(abs(num)))
    value = value[2:]
    for i in range(len(value)):
      if value[i] == '0':
        value[i] = '1'
      elif value[i] == '1': 
        value[i] = '0'
  code =  tostr(value)
  # size = size_codes[len(code)]
  # code = size+code
  return code

"""HUFFMAN oc AC"""

from heapq import heappush, heappop, heapify
from collections import defaultdict
 
def encode(symb2freq):
    heap = [[wt, [sym, ""]] for sym, wt in symb2freq.items()]
    heapify(heap)
    while len(heap) > 1:
        lo = heappop(heap)
        hi = heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))
 
lst = temp_d
symb2freq = defaultdict(int)
for ch in lst:
    symb2freq[ch] += 1
huff = encode(symb2freq)

value = list()
code = list()

huff_dict = dict()

for p in huff:
  value.append(p[0])
  code.append(p[1])
  huff_dict.update({p[0]:p[1]})

"""Till here, it is working fine, but did'nt do the final step to make it as single stream of bits. Huffman coding alogithm is working fine, Just have to do that for AC component."""

# bitstream = temp_d
# for i in range(len(temp_d)):
#   for j in range(len(value)) :
#     if value[j] == temp_d[i]:
#       bitstream[i] = code[j]

import sys
a = sys.getsizeof(bitstream)
b = sys.getsizeof(img)
print(a,b)