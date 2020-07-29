# device 2 is soundflower loopback audio ioq
#sox -d recording.wav

from __future__ import print_function
import sounddevice as sd 

import math, sys
from numpy import matrix
from numpy import linalg
import numpy as np

from scipy.linalg import hadamard
from scipy.linalg import solve


def modMatInv(A,p):       # Finds the inverse of matrix A mod p
  n=len(A)
  A=matrix(A)
  adj=np.zeros(shape=(n,n))
  for i in range(0,n):
    for j in range(0,n):
      adj[i][j]=((-1)**(i+j)*int(round(linalg.det(minor(A,j,i)))))%p
  return (modInv(int(round(linalg.det(A))),p)*adj)%p

def modInv(a,p):          # Finds the inverse of a mod p, if it exists
  for i in range(1,p):
    if (i*a)%p==1:
      return i
  raise ValueError(str(a)+" has no inverse mod "+str(p))

def minor(A,i,j):    # Return matrix A with the ith row and jth column deleted
  A=np.array(A)
  minor=np.zeros(shape=(len(A)-1,len(A)-1))
  p=0
  for s in range(0,len(minor)):
    if p==i:
      p=p+1
    q=0
    for t in range(0,len(minor)):
      if q==j:
        q=q+1
      minor[s][t]=A[p][q]
      q=q+1
    p=p+1
  return minor
  
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
 
* """.split("\n")[::-1]


h =   ((1+hadamard(8))/2)  % p
hinv = modMatInv( h, p ) 
pmax=[1]*8

( gain, threshold, duration , samplerate) = ( 0.125, 1, 10. ,   44100.0 )
tones= [ float(300*(3+mi)) for mi in range(1,1+len(msg))]

def callback(indata, outdata, frames, time, status): 
 global sidx, idx, tones, amplitude, pmax, mode

 t = (sidx + np.arange(frames)) / samplerate
 t = t.reshape(-1, 1)
 
 # generate output wave, from message column as vector 0,1,1,0,1,...  
 v = np.zeros(frames).reshape(-1,1) 
 if "D" not in mode:
  col = np.array( [ 1 if msg[mi][idx%len(msg[mi])] == '*' else 0 for mi in range(len(msg)) ] )
  if "g" in mode:
    col = h.dot( col.T ) # do the ghost
  if "m" in mode:
    col = (col + e ) % p  
  for ci in range(len(col)):
       carrier = col[ci]*np.sin(2 * np.pi * tones[ci] * t)
       v = v + carrier
  if "a" in mode:    
   outdata[:] = gain*v  
  else:   
   outdata[:] = v  
       
 # decode input data from microphone (tune to the tones)
 b = np.array(  [  abs( np.sum( indata * np.cos(2 * np.pi * tone * t)))  for   tone in tones ] )
 if "M" in mode:
  pmax=[ pmax[pi]  if pmax[pi]>b[pi] else  b[pi]   for pi in range(len(pmax)) ]
  b  = ( p  + ( (3*b)//(1+np.array(pmax))  ) ) % p
 if "X" in mode:
  b = ( hinv.dot( (b -e )%p ) ) % p   
 if "G" in mode:
  b = solve( h, b )
 print (";".join( [ "%6.2f" % abs(xx) for xx in b ] ))
 
 (sidx,idx) = (sidx+frames,idx+1)

(sidx,idx) = (0,0)  
with sd.Stream(channels=1, callback=callback , device=2  ): #, device=2 ): # device 2 is soundflower
 sd.sleep(int(duration * 1000))


