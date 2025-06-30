import spidev
import RPi.GPIO as GPIO
import time

# SPI and GPIO config
SPI_BUS = 0
SPI_DEVICE = 0
CS_PIN = 8  # GPIO8 (CE0)
GPIO.setmode(GPIO.BCM)
GPIO.setup(CS_PIN, GPIO.OUT)

# Initialize SPI
spi = spidev.SpiDev()
spi.open(SPI_BUS, SPI_DEVICE)
spi.max_speed_hz = 1000000

# --- Register access ---
def read_register(spi, cs_pin, reg_addr, length):
    header = [reg_addr & 0x7F]
    dummy_bytes = [0x00] * length
    GPIO.output(cs_pin, GPIO.LOW)
    resp = spi.xfer2(header + dummy_bytes)
    GPIO.output(cs_pin, GPIO.HIGH)
    return resp[1:]

def write_register(spi, cs_pin, reg_addr, data):
    header = [reg_addr | 0x80]
    GPIO.output(cs_pin, GPIO.LOW)
    spi.xfer2(header + data)
    GPIO.output(cs_pin, GPIO.HIGH)

# --- Constants ---
SYS_STATUS_REG = 0x0F
RXOK_BIT = 0x20  # Bit 5 = RX frame OK
RX_BUFFER_REG = 0x13
SYS_CTRL_REG = 0x0D
RXENAB = 0x01  # Enable RX

# --- RX setup ---
def enable_rx(spi, cs_pin):
    write_register(spi, cs_pin, SYS_CTRL_REG, [RXENAB])

def clear_status(spi, cs_pin):
    # Clear SYS_STATUS flags by writing 1s to bits you want to clear
    write_register(spi, cs_pin, SYS_STATUS_REG, [0xFF, 0xFF, 0xFF, 0xFF])

# --- Receiver main loop ---
try:
    print("Listening for UWB beacons...")
    while True:
        enable_rx(spi, CS_PIN)
        time.sleep(0.01)  # Wait for frame to arrive

        status = read_register(spi, CS_PIN, SYS_STATUS_REG, 4)
        if status[3] & RXOK_BIT:
            # Read received frame (assume small frame size)
            frame = read_register(spi, CS_PIN, RX_BUFFER_REG, 12)
            print(f"Received frame: {frame}")
            clear_status(spi, CS_PIN)

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopped")
finally:
    spi.close()
    GPIO.cleanup()
