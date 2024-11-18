import sys
import os
import logging
import time
import subprocess
from pillow import Image,ImageDraw,ImageFont
import traceback
from ctypes import *

class RaspberryPi:
    # Pin definition
    RST_PIN  = 17
    DC_PIN   = 25
    CS_PIN   = 8
    BUSY_PIN = 24
    PWR_PIN  = 18
    MOSI_PIN = 10
    SCLK_PIN = 11

    def __init__(self):
        import spidev
        import gpiozero

        self.SPI = spidev.SpiDev()
        self.GPIO_RST_PIN    = gpiozero.LED(self.RST_PIN)
        self.GPIO_DC_PIN     = gpiozero.LED(self.DC_PIN)
        self.GPIO_PWR_PIN    = gpiozero.LED(self.PWR_PIN)
        self.GPIO_BUSY_PIN   = gpiozero.Button(self.BUSY_PIN, pull_up = False)



    def digital_write(self, pin, value):
        if pin == self.RST_PIN:
            if value:
                self.GPIO_RST_PIN.on()
            else:
                self.GPIO_RST_PIN.off()
        elif pin == self.DC_PIN:
            if value:
                self.GPIO_DC_PIN.on()
            else:
                self.GPIO_DC_PIN.off()

        elif pin == self.PWR_PIN:
            if value:
                self.GPIO_PWR_PIN.on()
            else:
                self.GPIO_PWR_PIN.off()

    def digital_read(self, pin):
        if pin == self.BUSY_PIN:
            return self.GPIO_BUSY_PIN.value
        elif pin == self.RST_PIN:
            return self.RST_PIN.value
        elif pin == self.DC_PIN:
            return self.DC_PIN.value
        elif pin == self.PWR_PIN:
            return self.PWR_PIN.value

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes(data)

    def spi_writebyte2(self, data):
        self.SPI.writebytes2(data)

    def DEV_SPI_write(self, data):
        self.DEV_SPI.DEV_SPI_SendData(data)

    def DEV_SPI_nwrite(self, data):
        self.DEV_SPI.DEV_SPI_SendnData(data)

    def DEV_SPI_read(self):
        return self.DEV_SPI.DEV_SPI_ReadData()

    def module_init(self, cleanup=False):
        self.GPIO_PWR_PIN.on()
        
        if cleanup:
            find_dirs = [
                os.path.dirname(os.path.realpath(__file__)),
                '/usr/local/lib',
                '/usr/lib',
            ]
            self.DEV_SPI = None
            for find_dir in find_dirs:
                val = int(os.popen('getconf LONG_BIT').read())
                logging.debug("System is %d bit"%val)
                if val == 64:
                    so_filename = os.path.join(find_dir, 'DEV_Config_64.so')
                else:
                    so_filename = os.path.join(find_dir, 'DEV_Config_32.so')
                if os.path.exists(so_filename):
                    self.DEV_SPI = CDLL(so_filename)
                    break
            if self.DEV_SPI is None:
                RuntimeError('Cannot find DEV_Config.so')

            self.DEV_SPI.DEV_Module_Init()

        else:
            # SPI device, bus = 0, device = 0
            self.SPI.open(0, 0)
            self.SPI.max_speed_hz = 4000000
            self.SPI.mode = 0b00
        return 0

    def module_exit(self, cleanup=False):
        logger.debug("spi end")
        self.SPI.close()

        self.GPIO_RST_PIN.off()
        self.GPIO_DC_PIN.off()
        self.GPIO_PWR_PIN.off()
        logger.debug("close 5V, Module enters 0 power consumption ...")
        
        if cleanup:
            self.GPIO_RST_PIN.close()
            self.GPIO_DC_PIN.close()
            self.GPIO_PWR_PIN.close()
            self.GPIO_BUSY_PIN.close()

implementation = RaspberryPi()

for func in [x for x in dir(implementation) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))

# Display resolution
EPD_WIDTH       = 800
EPD_HEIGHT      = 480

logger = logging.getLogger(__name__)

class EPD:
    def __init__(self):
        self.reset_pin = RST_PIN
        self.dc_pin = DC_PIN
        self.busy_pin = BUSY_PIN
        self.cs_pin = CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
    
    Voltage_Frame_7IN5_V2 = [
        0x6, 0x3F, 0x3F, 0x11, 0x24, 0x7, 0x17,
    ]

    LUT_VCOM_7IN5_V2 = [
        0x0,    0xF,    0xF,    0x0,    0x0,    0x1,
        0x0,    0xF,    0x1,    0xF,    0x1,    0x2,
        0x0,    0xF,    0xF,    0x0,    0x0,    0x1,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
    ]

    LUT_WW_7IN5_V2 = [
        0x10,   0xF,    0xF,    0x0,    0x0,    0x1,
        0x84,   0xF,    0x1,    0xF,    0x1,    0x2,
        0x20,   0xF,    0xF,    0x0,    0x0,    0x1,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
    ]

    LUT_BW_7IN5_V2 = [
        0x10,   0xF,    0xF,    0x0,    0x0,    0x1,
        0x84,   0xF,    0x1,    0xF,    0x1,    0x2,
        0x20,   0xF,    0xF,    0x0,    0x0,    0x1,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
    ]

    LUT_WB_7IN5_V2 = [
        0x80,   0xF,    0xF,    0x0,    0x0,    0x1,
        0x84,   0xF,    0x1,    0xF,    0x1,    0x2,
        0x40,   0xF,    0xF,    0x0,    0x0,    0x1,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
    ]

    LUT_BB_7IN5_V2 = [
        0x80,   0xF,    0xF,    0x0,    0x0,    0x1,
        0x84,   0xF,    0x1,    0xF,    0x1,    0x2,
        0x40,   0xF,    0xF,    0x0,    0x0,    0x1,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
        0x0,    0x0,    0x0,    0x0,    0x0,    0x0,
    ]

    Lut_all_fresh = [0x67,        0xBF,   0x3F,   0x0D,   0x00,   0x1C,
    #VCOM
    0x00,       0x32,   0x32,   0x00,   0x00,   0x01,
    0x00,       0x0A,   0x0A,   0x00,   0x00,   0x00,
    0x00,       0x28,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    #WW
    0x60,       0x32,   0x32,   0x00,   0x00,   0x01,
    0x60,       0x0A,   0x0A,   0x00,   0x00,   0x00,
    0x80,       0x28,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    #BW
    0x60,       0x32,   0x32,   0x00,   0x00,   0x01,
    0x60,       0x0A,   0x0A,   0x00,   0x00,   0x00,
    0x80,       0x28,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    #WB
    0x90,       0x32,   0x32,   0x00,   0x00,   0x01,
    0x60,       0x0A,   0x0A,   0x00,   0x00,   0x00,
    0x40,       0x28,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    #BB
    0x90,       0x32,   0x32,   0x00,   0x00,   0x01,
    0x60,       0x0A,   0x0A,   0x00,   0x00,   0x00,
    0x40,       0x28,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    #Reserved
    0xFF,       0xFF,   0xFF,   0xFF,   0xFF,   0xFF,
    0xFF,       0xFF,   0xFF,   0xFF,   0xFF,   0xFF,
    0xFF,       0xFF,   0xFF,   0xFF,   0xFF,   0xFF,
    0xFF,       0xFF,   0xFF,   0xFF,   0xFF,   0xFF,
    0xFF,       0xFF,   0xFF,   0xFF,   0xFF,   0xFF,
    0xFF,
    ]

    Lut_partial=[0x67,  0xBF,   0x3F,   0x0D,   0x00,   0x1C,
    #VCOM
    0x00,       0x14,   0x02,   0x00,   0x00,   0x01,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    #WW
    0x20,       0x14,   0x02,   0x00,   0x00,   0x01,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    #BW
    0x80,       0x14,   0x02,   0x00,   0x00,   0x01,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    #WB
    0x40,       0x14,   0x02,   0x00,   0x00,   0x01,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    #BB
    0x00,       0x14,   0x02,   0x00,   0x00,   0x01,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,       0x00,   0x00,   0x00,   0x00,   0x00,
    #Reserved
    0xFF,       0xFF,   0xFF,   0xFF,   0xFF,   0xFF,
    0xFF,       0xFF,   0xFF,   0xFF,   0xFF,   0xFF,
    0xFF,       0xFF,   0xFF,   0xFF,   0xFF,   0xFF,
    0xFF,       0xFF,   0xFF,   0xFF,   0xFF,   0xFF,
    0xFF,       0xFF,   0xFF,   0xFF,   0xFF,   0xFF,
    0xFF,
    ]

    # Hardware reset
    def reset(self):
        digital_write(self.reset_pin, 1)
        delay_ms(20) 
        digital_write(self.reset_pin, 0)
        delay_ms(2)
        digital_write(self.reset_pin, 1)
        delay_ms(20)   

    def send_command(self, command):
        digital_write(self.dc_pin, 0)
        digital_write(self.cs_pin, 0)
        spi_writebyte([command])
        digital_write(self.cs_pin, 1)

    def send_data(self, data):
        digital_write(self.dc_pin, 1)
        digital_write(self.cs_pin, 0)
        spi_writebyte([data])
        digital_write(self.cs_pin, 1)

    def send_data2(self, data):
        digital_write(self.dc_pin, 1)
        digital_write(self.cs_pin, 0)
        spi_writebyte2(data)
        digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        self.send_command(0x71)
        busy = digital_read(self.busy_pin)
        while(busy == 0):
            self.send_command(0x71)
            busy = digital_read(self.busy_pin)
        delay_ms(20)
        logger.debug("e-Paper busy release")
        
    def SetLut(self, lut_vcom, lut_ww, lut_bw, lut_wb, lut_bb):
        self.send_command(0x20)
        for count in range(0, 42):
            self.send_data(lut_vcom[count])

        self.send_command(0x21)
        for count in range(0, 42):
            self.send_data(lut_ww[count])

        self.send_command(0x22)
        for count in range(0, 42):
            self.send_data(lut_bw[count])

        self.send_command(0x23)
        for count in range(0, 42):
            self.send_data(lut_wb[count])

        self.send_command(0x24)
        for count in range(0, 42):
            self.send_data(lut_bb[count])

    def init(self):
        if (module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()

        self.send_command(0x01)     # power setting
        self.send_data(0x17)        # 1-0=11: internal power
        self.send_data(self.Voltage_Frame_7IN5_V2[6])   # VGH&VGL
        self.send_data(self.Voltage_Frame_7IN5_V2[1])   # VSH
        self.send_data(self.Voltage_Frame_7IN5_V2[2])   # VSL
        self.send_data(self.Voltage_Frame_7IN5_V2[3])   # VSHR
        
        self.send_command(0x82)     # VCOM DC Setting
        self.send_data(self.Voltage_Frame_7IN5_V2[4])   # VCOM

        self.send_command(0x06)     # Booster Setting
        self.send_data(0x27)
        self.send_data(0x27)
        self.send_data(0x2F)
        self.send_data(0x17)
        
        self.send_command(0x30)     # OSC Setting
        self.send_data(self.Voltage_Frame_7IN5_V2[0])   # 3C=50Hz, 3A=100HZ

        self.send_command(0x04)     # POWER ON
        delay_ms(100)
        self.ReadBusy()

        self.send_command(0X00)     # PANNEL SETTING
        self.send_data(0x3F)        # KW-3f KWR-2F BWROTP-0f BWOTP-1f

        self.send_command(0x61)     # tres
        self.send_data(0x03)        # source 800
        self.send_data(0x20)
        self.send_data(0x01)        # gate 480
        self.send_data(0xE0)

        self.send_command(0X15)
        self.send_data(0x00)

        self.send_command(0X50)     # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x10)
        self.send_data(0x07)

        self.send_command(0X60)     # TCON SETTING
        self.send_data(0x22)

        self.send_command(0x65)     # Resolution setting
        self.send_data(0x00)
        self.send_data(0x00)        # 800*480
        self.send_data(0x00)
        self.send_data(0x00)

        self.SetLut(self.LUT_VCOM_7IN5_V2, self.LUT_WW_7IN5_V2, self.LUT_BW_7IN5_V2, self.LUT_WB_7IN5_V2, self.LUT_BB_7IN5_V2)
        # EPD hardware init end
        return 0
    
    def Epaper_LUT_By_MCU(self,wavedata):

        VCEND=wavedata[0]&0x08
        BDEND=(wavedata[1]&0xC0)>>6
        EVS=VCEND|BDEND
        PLL=(wavedata[0]&0xF0)>>4
        XON=wavedata[2]&0xC0

        self.send_command(0x52)       #EVS
        self.send_data(EVS)

        self.send_command(0x30)                   #PLL setting 
        self.send_data(PLL)

        self.send_command(0x01)       #Set VGH VGL VSH VSL VSHR
        self.send_data (0x17)
        self.send_data (wavedata[0]&0x07)       #VGH/VGL Voltage Level selection
        self.send_data (wavedata[1]&0x3F)               #VSH for black
        self.send_data (wavedata[2]&0x3F)       #VSL for white
        self.send_data (wavedata[3]&0x3F)       #VSHR for red

        self.send_command(0x2A)       #LUTOPT
        self.send_data(XON)
        self.send_data(wavedata[4])

        self.send_command(0x82)       #VCOM_DC setting
        self.send_data (wavedata[5])  #Vcom value


        self.send_command(0x20)
        self.send_data2(wavedata[6:48])

        self.send_command(0x21)
        self.send_data2(wavedata[48:90])

        self.send_command(0x22)
        self.send_data2(wavedata[90:132])

        self.send_command(0x23)
        self.send_data2(wavedata[132:174])

        self.send_command(0x24)
        self.send_data2(wavedata[174:216])

    def init2(self):
        if (module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()

        self.send_command(0x00)  # Panel setting   
        self.send_data(0x3F)

        self.send_command(0x06)  # Booster Setting
        self.send_data(0x17)  
        self.send_data(0x17)
        self.send_data(0x28)
        self.send_data(0x18)

        self.send_command(0x50)  # VCOM and DATA interval setting    
        self.send_data(0x22)
        self.send_data(0x07)

        self.send_command(0x60)  # TCON setting
        self.send_data(0x22)  # S-G G-S

        self.send_command(0x61)  # Resolution setting
        self.send_data(0x03)#800*480
        self.send_data(0x20)
        self.send_data(0x01)
        self.send_data(0xE0) 

        self.send_command(0x65)  # Resolution setting
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x04) #POWER ON
        delay_ms(100)
        self.ReadBusy() 

        return 0

    def init_fast(self):
        self.init2()
        self.Epaper_LUT_By_MCU(self.Lut_all_fresh)
        return 0
    

    def init_part(self):
        self.init2()
        self.Epaper_LUT_By_MCU(self.Lut_partial)
        return 0
    

    def getbuffer(self, image):
        img = image
        imwidth, imheight = img.size
        if(imwidth == self.width and imheight == self.height):
            img = img.convert('1')
        elif(imwidth == self.height and imheight == self.width):
            # image has correct dimensions, but needs to be rotated
            img = img.rotate(90, expand=True).convert('1')
        else:
            logger.warning("Wrong image dimensions: must be " + str(self.width) + "x" + str(self.height))
            # return a blank buffer
            return [0x00] * (int(self.width/8) * self.height)

        buf = bytearray(img.tobytes('raw'))
        # The bytes need to be inverted, because in the PIL world 0=black and 1=white, but
        # in the e-paper world 0=white and 1=black.
        for i in range(len(buf)):
            buf[i] ^= 0xFF
        return buf

    def display(self, image):
        if(self.width % 8 == 0):
            Width = self.width // 8
        else:
            Width = self.width // 8 +1
        Height = self.height
        image1 = [0xFF] * int(self.width * self.height / 8)
        for j in range(Height):
                for i in range(Width):
                    image1[i + j * Width] = ~image[i + j * Width]
        self.send_command(0x10)
        self.send_data2(image1)

        self.send_command(0x13)
        self.send_data2(image)

        self.send_command(0x12)
        delay_ms(100)
        self.ReadBusy()

    def Clear(self):
        self.send_command(0x10)
        self.send_data2([0xFF] * int(self.width * self.height / 8))
        self.send_command(0x13)
        self.send_data2([0x00] * int(self.width * self.height / 8))
        self.send_command(0x12)
        delay_ms(100)
        self.ReadBusy()

    def display_Partial(self, Image, Xstart, Ystart, Xend, Yend):
        if((Xstart % 8 + Xend % 8 == 8 & Xstart % 8 > Xend % 8) | Xstart % 8 + Xend % 8 == 0 | (Xend - Xstart)%8 == 0):
            Xstart = Xstart // 8 * 8
            Xend = Xend // 8 * 8
        else:
            Xstart = Xstart // 8 * 8
            if Xend % 8 == 0:
                Xend = Xend // 8 * 8
            else:
                Xend = Xend // 8 * 8 + 1
                
        Width = (Xend - Xstart) // 8
        Height = Yend - Ystart

        self.send_command(0x50)
        self.send_data(0xA9)
        self.send_data(0x07)

        self.send_command(0x91)         # This command makes the display enter partial mode
        self.send_command(0x90)         # resolution setting
        self.send_data (Xstart//256)
        self.send_data (Xstart%256)   #x-start    

        self.send_data ((Xend-1)//256)
        self.send_data ((Xend-1)%256)  #x-end

        self.send_data (Ystart//256)  #
        self.send_data (Ystart%256)   #y-start    

        self.send_data ((Yend-1)//256)
        self.send_data ((Yend-1)%256)  #y-end
        self.send_data (0x01)

        image1 = [0xFF] * int(self.width * self.height / 8)
        for j in range(Height):
                for i in range(Width):
                    image1[i + j * Width] = ~Image[i + j * Width]

        self.send_command(0x13)   #Write Black and White image to RAM
        self.send_data2(image1)

        self.send_command(0x12)
        delay_ms(100)
        self.ReadBusy()

    def sleep(self):
        self.send_command(0x02) # POWER_OFF
        self.ReadBusy()
        
        self.send_command(0x07) # DEEP_SLEEP
        self.send_data(0XA5)
        
        delay_ms(2000)
        module_exit()

