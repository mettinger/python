import pyshark
import pickle

counter = 0

def myCallback(pkt):
    global counter

    protocolName = pkt[-1].layer_name
    if not protocolName in protocolSet:
        print('\n' + protocolName + '\n')
        protocolSet.add(pkt[-1].layer_name)
        packetList.append(pkt)
        
        with open('protocolList.txt', 'w') as f:
            f.write(str(protocolSet))

        with open('protocolPackets.pkl', 'wb') as f:
            pickle.dump(packetList, f)

        
    if counter % 10000 == 0:
        print(counter)
    counter = counter + 1

try:
    with open('protocolList.txt', 'r') as f:
        protocolSet = eval(f.readline())
except:
    protocolSet = set()

try:
    with open('protocolPackets.pkl', 'rb') as f:
        packetList = pickle.load(f)
except:
    packetList = []

capture = pyshark.LiveCapture()
capture.apply_on_packets(myCallback)
