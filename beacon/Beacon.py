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
spi.max_speed_hz = 1000000  # You can raise this to 20MHz later

# --- Helper functions ---
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

# --- Beacon frame ---
def create_blink_frame(seq_num):
    return [
        0xC5,         # Frame control: blink frame
        seq_num & 0xFF,  # Sequence number
        0xDE, 0xAD, 0xBE, 0xEF,  # EUI part 1
        0xCA, 0xFE, 0x00, 0x01   # EUI part 2 (8 bytes total)
    ]

def send_beacon(spi, cs_pin, seq_num):
    TX_BUFFER_REG = 0x12
    SYS_CTRL_REG = 0x0D
    TXSTRT = 0x02  # Bit to trigger TX

    blink = create_blink_frame(seq_num)
    write_register(spi, cs_pin, TX_BUFFER_REG, blink)
    time.sleep(0.01)  # short delay before trigger

    write_register(spi, cs_pin, SYS_CTRL_REG, [TXSTRT])
    print(f"Sent beacon seq={seq_num}")

# --- Main loop ---
try:
    print("Starting DWM3000 Beacon")
    seq = 0
    while True:
        send_beacon(spi, CS_PIN, seq)
        seq += 1
        time.sleep(1)  # 1 Hz beacon rate

except KeyboardInterrupt:
    print("Exiting...")
finally:
    spi.close()
    GPIO.cleanup()
