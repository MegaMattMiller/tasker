# Bus 003 Device 003: ID 0fe6:811e ICS Advent Parallel Adapter
# lsusb -vvv -d 0fe6:811e | grep iInterface
# iInterface              0 
# lsusb -vvv -d 0fe6:811e | grep bEndpointAddress | grep OUT
# bEndpointAddress     0x01  EP 1 OUT
from datetime import datetime
from escpos import *
from dateutil import tz
import sys,json

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

def printTask(taskName, taskDesc, createdAt, assignedTo):

    utc = datetime.strptime(createdAt, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    date = central.date().strftime("%m-%d-%Y")
    time = central.time().strftime("%I:%M %p")

    p = printer.Usb(0x0fe6, 0x811e)
    p.text(f'{assignedTo}\n')
    p.text('\n')
    p.text('Created\n')
    p.text(f'{date} at {time}\n')
    p.text('\n')
    p.text('--------------------\n')
    p.text('\n')
    p.text(f'{taskName}\n')
    p.text('\n')
    p.text('--------------------\n')
    p.text('\n')
    p.text(f'{taskDesc}\n')
    p.text('\n')
    p.cut()

if __name__ == "__main__":
    inputs = json.loads(sys.argv[1])
    printTask(inputs['taskName'], inputs['taskDesc'], inputs['createdAt'], inputs['assignedTo'])