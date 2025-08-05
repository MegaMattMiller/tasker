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
import PIL.Image
import base64
from io import BytesIO

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

options = {
    'width': 256,
}

def create_task_html(inputs):    

    createdAt = inputs['createdAt']
    assignedTo = inputs['assignedTo']
    taskName = inputs['taskName']
    taskDesc = inputs['taskDesc']
    taskUrl = inputs['url']
    fact = inputs['fact']

    utc = datetime.strptime(createdAt, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    date = central.date().strftime("%m-%d-%Y")
    time = central.time().strftime("%I:%M %p")

    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )
    qr.add_data(taskUrl)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    with open('styles.css', 'r') as f:
        styles = f.read()
        f.close()

    html_content = f"""
    <!DOCTYPE html>
<html>

<head>
  <meta charset="UTF-8">
  <style>
  {styles}
  </style>
</head>

<body>
  <div class="ticket-container">
    <!-- Task Title -->
    <div class="label">Title:</div>
    <div class="task-title">
      <p>{taskName}</p>
    </div>

    <!-- Dashed Separator -->
    <br />
    <div class="dashed-line"></div>
    <br />

    <!-- Assigned -->
    <div class="label">Assigned to:</div>
    <div class="task-assigned">
      <p>{assignedTo}</p>
    </div>

    <!-- Dashed Separator -->
    <br />
    <div class="dashed-line"></div>
    <br />

    <!-- Due Date Section -->
    <div class="label">Created:</div>
    <div class="due-date-text">
      <p>{date} at {time}</p>
    </div>

    <!-- Dashed Separator -->
    <br />
    <div class="dashed-line"></div>
    <br />

    <!-- Task Description -->
    <div class="label">Description:</div>
    <div class="task-description">
      <p>{taskDesc}</p>
    </div>

    <!-- Dashed Separator -->
    <br />
    <div class="dashed-line"></div>
    <br />

    <!-- Task URL -->
    <div class="task-url">
      <p>{taskUrl}</p>
    </div>

    <img class="qr" src="data:image/jpeg;base64,{img_str}" />

    <!-- Dashed Separator -->
    <br />
    <div class="dashed-line"></div>
    <br />

    <!-- Task Description -->
    <div class="fact">Fun fact:</div>
    <div class="fact">
      <p>{fact}</p>
    </div>

    <!-- Bottom Perforation -->
    <!-- <div class="perforation bottom-perforation"></div> -->
  </div>
</body>

</html>
    """
    
    return html_content

def create_task_html_image(inputs):
    print("Creating task HTML...")

    """Create task card image from HTML using available method."""
    html_content = create_task_html(inputs)

    print("Creating task HTML image...")

    # Try imgkit first (faster), then Selenium
    image_path = html_to_image_imgkit(html_content)
    
    return image_path

def html_to_image_imgkit(html_content):
    
    try:
        
        # Configure options for thermal printer size
        options = {
            'width': 576,  # 72mm thermal printer width
            'disable-smart-width': '',
            'encoding': 'UTF-8',
            'disable-local-file-access': '',
            'crop-w': 576,  # Crop to exact width
        }
        
        # Try to configure wkhtmltopdf path for Windows
        config = None
        import os
        possible_paths = [
            r'/usr/bin/wkhtmltoimage',
            r'/usr/bin/',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                config = imgkit.config(wkhtmltoimage=path)
                break

        
        # Convert HTML to image
        imgkit.from_string(html_content, 'out.png', options=options, config=config)
        
        return 'out.png'
        
    except Exception as e:
        print(f"Error converting HTML to image with imgkit: {str(e)}")
        return None

def printTask(inputs):
    createdAt = inputs['createdAt']
    assignedTo = inputs['assignedTo']
    taskName = inputs['taskName']
    taskDesc = inputs['taskDesc']
    taskUrl = inputs['url']
    fact = inputs['fact']

    utc = datetime.strptime(createdAt, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    date = central.date().strftime("%m-%d-%Y")
    time = central.time().strftime("%I:%M %p")

    # img = qrcode.make(taskUrl)
    # img.save("my_qrcode.png")

    # imgkit.from_url('https://google.com', 'out.png', options=options)

    p = printer.Usb(0x0fe6, 0x811e)
    p.textln('Assigned to:')
    p.textln(f'{assignedTo}')
    p.ln(1)
    p.textln('Created:')
    p.textln(f'{date} at {time}')
    p.ln(1)
    p.textln('--------------------')
    p.ln(1)
    p.text(f'{taskName}')
    p.ln(1)
    p.textln('--------------------')
    p.ln(1)
    p.textln(f'{taskDesc}')
    p.textln('--------------------')
    p.ln(1)
    p.textln(f'{taskUrl}')
    p.qr(taskUrl, ec=3, size=10, model=2, native=False)
    # p.image('out.png', impl='bitImageRaster', center=False)
    p.ln(1)
    p.textln('Fun fact:')
    p.textln(f'{fact}')
    p.ln(1)
    p.cut()

    print(taskUrl)

def printTaskImage(path, inputs):
    createdAt = inputs['createdAt']
    assignedTo = inputs['assignedTo']
    taskName = inputs['taskName']
    taskDesc = inputs['taskDesc']
    taskUrl = inputs['url']
    fact = inputs['fact']

    utc = datetime.strptime(createdAt, "%Y-%m-%dT%H:%M:%S.%fZ")
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    date = central.date().strftime("%m-%d-%Y")
    time = central.time().strftime("%I:%M %p")
    
    p = printer.Usb(0x0fe6, 0x811e)
    p.image(path, impl='bitImageRaster', center=True)
    # p.image('out.png', impl='bitImageRaster', center=False)
    p.ln(2)
    p.cut()

if __name__ == "__main__":
    inputs = json.loads(sys.argv[1])
    # printTask(inputs)
    create_task_html_image(inputs)
    printTaskImage('out.png', inputs)
