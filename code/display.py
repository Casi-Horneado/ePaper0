#!/usr/bin/python
# -*- coding:utf-8 -*-

display_image = 'image.jpg'

from local_epaper_fns import *
logging.basicConfig(level=logging.DEBUG)

try:

## initiate logs
    logging.info("e-paper log")
## define function
    epd = EPD()
    logging.info("init and Clear")
    epd.init_part() #epd.init_fast() #epd.init()
    epd.Clear()
## userinputs
    new_size = 360
    frame_width = epd.width
    frame_height = epd.height
    x_offset = (frame_width - new_size) // 2
    y_offset = (frame_height - new_size) // 2
    display_text = 'casi horneado'


    img = Image.open(os.path.join(display_image))
## resize file
    resized_image = img.resize((new_size, new_size), Image.LANCZOS) #.save(os.path.join('resized.jpg')

## Create a new 800x480 image
    new_image = Image.new('1', (frame_width, frame_height), color=0)

## Paste the smaller image into the center of the new image
    new_image.paste(resized_image, (x_offset, y_offset))

## the fonts are default right now
    font48 = ImageFont.truetype('Font.ttc', 48)
    
    draw = ImageDraw.Draw(new_image)
## add (centered) text
    _, _, w, h = draw.textbbox((0, 0), display_text, font = font48)
    draw.text(((frame_width-w)/2, 20), display_text, font = font48, fill = 255)
## display image
    epd.display(epd.getbuffer(new_image))
    time.sleep(2)

    logging.info("Clear...")
    epd.init()
    epd.Clear()
    epd.init()
    epd.Clear()

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    module_exit(cleanup=True)
    exit()

