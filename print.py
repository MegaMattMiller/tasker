# Bus 003 Device 003: ID 0fe6:811e ICS Advent Parallel Adapter
# lsusb -vvv -d 0fe6:811e | grep iInterface
# iInterface              0 
# lsusb -vvv -d 0fe6:811e | grep bEndpointAddress | grep OUT
# bEndpointAddress     0x01  EP 1 OUT
from datetime import datetime
from escpos import *
from dateutil import tz
import qrcode
import sys,json
import imgkit

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

options = {
    'width': 256,
}

def printTask(taskName, taskDesc, createdAt, assignedTo, taskUrl):

    utc = datetime.strptime(createdAt, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    date = central.date().strftime("%m-%d-%Y")
    time = central.time().strftime("%I:%M %p")

    # img = qrcode.make(taskUrl)
    # img.save("my_qrcode.png")

    # imgkit.from_url('https://google.com', 'out.png', options=options)

    p = printer.Usb(0x0fe6, 0x811e)
    p.text('Assigned to:\n')
    p.text(f'{assignedTo}\n')
    p.text('\n')
    p.text('Created:\n')
    p.text(f'{date} at {time}\n')
    p.text('\n')
    p.text('--------------------\n')
    p.text('\n')
    p.text(f'{taskName}\n')
    p.text('\n')
    p.text('--------------------\n')
    p.text('\n')
    p.text(f'{taskDesc}\n')
    p.text('--------------------\n')
    p.text('\n')
    p.text(f'{taskUrl}\n')
    p.qr(taskUrl, ec=3, size=10, model=2, native=False)
    p.text('\n')
    p.text('\n')
    # p.image('out.png', impl='bitImageRaster', center=False)
    p.text('\n')
    p.cut()

    print(taskUrl)

if __name__ == "__main__":
    inputs = json.loads(sys.argv[1])
    printTask(inputs['taskName'], inputs['taskDesc'], inputs['createdAt'], inputs['assignedTo'], inputs['url'])