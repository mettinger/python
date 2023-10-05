import pyshark
capture = pyshark.LiveCapture(interface='Wi-Fi')

for packet in capture.sniff_continuously():
    print ('Just arrived:', packet)