# NOT YET IMPLEMENTED
# NOT YET IMPLEMENTED
# NOT YET IMPLEMENTED
# NOT YET IMPLEMENTED


hanlde_pluto_sdr="""
export PATH=$PATH:/Users/h.j.eleas/Documents/hardware/libiio/iio.framework/Tools/
iio_info -s

# send and receive on 1 GHZ other: 438M200 Hz (70cm band)
iio_attr -a -c ad9361-phy TX_LO frequency 438200000 #1000000000
iio_attr -a -c ad9361-phy RX_LO frequency 438200000 #1000000000
iio_attr -a -c -o ad9361-phy voltage0 sampling_frequency 3000000
iio_attr -a -c -o ad9361-phy voltage0 rf_bandwidth 5000000
iio_attr -a -c -o ad9361-phy voltage0 gain_control_mode 'slow_attack'
iio_attr -a -c -o ad9361-phy voltage0 hardwaregain '-10'

# generate waveform, carriers on 60k, 70k, 80k Hz
python hellIQ.py todevice samples_todevice.raw

# use the reentrant IP stack of PLUTO (not USB control mode)
cat samples_todevice.raw | iio_writedev -c -u ip:192.168.2.1  -b 32768 cf-ad9361-dds-core-lpc &
iio_readdev -u ip:192.168.2.1  -b 32768 cf-ad9361-lpc | pv >samples_fromdevice.raw

# make a nice plot
python hellIQ.py toplot samples_fromdevice.raw
open hell.png
"""


import sys
import numpy as np
import numpy as np
import matplotlib.pyplot as plt

# User configurable
TXLO = 1000000000
TXBW = 5000000
TXFS = 3000000
RXLO = TXLO
RXBW = TXBW
RXFS = TXFS


samples_per_channel = 2**15

# Generate a sinewave waveform
ts = 1/float(RXFS)
t = np.arange(0, samples_per_channel*ts, ts)

carriers = [  1e5, 1.5e5 , 1.2e5, 3e5 ]
i = np.zeros(len(t))
q = np.zeros(len(t))
for fc in carriers:
 i = i + np.sin(2*np.pi*t*fc)* 2**13 
 q = q + np.cos(2*np.pi*t*fc)* 2**13 
 
iq = np.empty((i.size + q.size,), dtype=i.dtype)
iq[0::2] = i
iq[1::2] = q
iq = np.int16(iq) # 131072/(2^15) =  4 bytes per sample (2 bytes I and 2 bytes Q)

with open("samples_writedev.raw","wb") as fout: # Send data to buffer
 fout.write(bytearray(iq))
 fout.close()
