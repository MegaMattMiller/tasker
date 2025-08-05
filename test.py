# Bus 003 Device 003: ID 0fe6:811e ICS Advent Parallel Adapter
# lsusb -vvv -d 0fe6:811e | grep iInterface
# iInterface              0
# lsusb -vvv -d 0fe6:811e | grep bEndpointAddress | grep OUT
# bEndpointAddress     0x01  EP 1 OUT
from escpos import *
import sys,json

def printTask(taskName, taskDesc, createdAt, assignedTo):
    p = printer.Usb(0x0fe6, 0x811e)
    p.text(f'{assignedTo}\n')
    p.text('\n')
    p.text(f'{createdAt}\n')
    p.text('\n')
    p.text(f'{taskName}\n')
    p.text('\n')
    p.text(f'{taskDesc}\n')
    p.text('\n')
    p.cut()

if __name__ == "__main__":
    inputs = json.loads(sys.argv[1])
    printTask(inputs['taskName'], inputs['taskDesc'], inputs['createdAt'], inputs['assignedTo'])
