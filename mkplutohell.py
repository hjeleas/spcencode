# hell-o-ween, SDR version - outputs I/Q data 
# to plot:
# python iqplot.py  -fw 4096  -f int16 -p spec hell.iq 
from __future__ import print_function

import sys
import numpy as np
import numpy as np
import matplotlib.pyplot as plt


from scipy.linalg import hadamard


# User configurable
TXLO = 1000000000
TXBW = 5000000
TXFS = 3000000
RXLO = TXLO
RXBW = TXBW
RXFS = TXFS


samples_per_channel = 2**12

p  = 3   # prime  
e = np.array( [0,0,0,0, 0,0,0,0] )
mode = ""
try:
  mode = sys.argv[1]
  e = np.array( [float(ei) for ei in  sys.argv[2].split(",") ] )
except IndexError:
  pass
print("e:%s mode:%s" % (e , mode), file=sys.stderr)
 
  
#pmax = [1]*8
msg=""" 
*  *  ****  *    *     **   *      * **** **** *   *     
*  *  *     *    *    *  *  *      * *    *    **  *     
****  ***   *    *    *  *   * ** *  ***   **  * * *     
*  *  *     *    *    *  *   * ** *  *    *    * * *     
*  *  ****  **** ****  **     *  *   **** **** *  **     
 
* """.split("\n")  #[::-1]


h =   ((1+hadamard(8))/2)  % p
carriers = [ float(1e5*(mi)) for mi in range(1,1+len(msg))]

# Generate a sinewave waveform
def mkticker( col, iq):
  global h, carriers,t

  (i,q) =    ( np.zeros(len(t)) , np.zeros(len(t)) )
  
  #print " ".join( [ " " if c ==0 else "*" for c in col])
  for fci in  range(len(carriers)):
    if col[ fci ]:
     i = i +  ( np.sin(2*np.pi*t*carriers[fci]) ) * 2**10 
     q = q +  ( np.cos(2*np.pi*t*carriers[fci]) ) * 2**10
    
  iq[0::2] = i
  iq[1::2] = q
 
 
ts = 1/float(RXFS)
t = np.arange(0, samples_per_channel*ts, ts)
(i,q) =    ( np.zeros(len(t)) , np.zeros(len(t)) )
iq = np.empty((2*samples_per_channel,), dtype=i.dtype)
slower = mode.count('/')
with open("hell.iq","wb") as fout: # Send data to buffer
 
 for idx in range(100):
   col = np.array( [ 1 if msg[mi][(idx/slower)%len(msg[mi])] == '*' else 0 for mi in range(len(msg)) ] )
   if "g" in mode:
     col = h.dot( col.T ) # do the ghost
   if "m" in mode:
     col = (col + e ) % p
       
   mkticker( col, iq )
   iq16 = np.int16( iq ) # 131072/(2^12) 
   t = t + samples_per_channel*ts
   #  4 bytes per sample (2 bytes I and 2 bytes Q)
   fout.write(bytearray(iq16)) 
   
 fout.close()


