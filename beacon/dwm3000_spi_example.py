import spidev
import RPi.GPIO as GPIO
import time

# Example SPI setup for DWM3000 (beacon)
SPI_BUS = 0
SPI_DEVICE = 0
CS_PIN = 8
IRQ_PIN = 17

spi = spidev.SpiDev()
spi.open(SPI_BUS, SPI_DEVICE)
spi.max_speed_hz = 1000000

GPIO.setmode(GPIO.BCM)
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.setup(IRQ_PIN, GPIO.IN)

# Example: Read device ID
GPIO.output(CS_PIN, GPIO.LOW)
resp = spi.xfer2([0x00, 0x00, 0x00, 0x00])
GPIO.output(CS_PIN, GPIO.HIGH)
print('DWM3000 response:', resp)

spi.close()
GPIO.cleanup()
