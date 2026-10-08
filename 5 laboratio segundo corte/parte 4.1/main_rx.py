# main_rx.py -> guardar como main.py en la Pico 2 (RECEPTOR)
# Necesita en la Pico: nrf24.py y ssd1306.py
from machine import Pin, SPI, I2C
import time
import ssd1306
from nrf24 import NRF24, RATES, POWER_DBM

# ---------- Configuración (debe coincidir con el transmisor) ----------
CHANNEL  = 40
POWER    = 3
RATE     = 1
CH_STEP  = 4
AUTO_ACK = True
CHUNK    = 28

# ---------- Hardware ----------
i2c  = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
spi  = SPI(0, baudrate=1_000_000, polarity=0, phase=0,
           sck=Pin(18), mosi=Pin(19), miso=Pin(16))
radio = NRF24(spi, csn=17, ce=20, channel=CHANNEL, power=POWER,
              rate=RATE, auto_ack=AUTO_ACK)

btn_ch  = Pin(10, Pin.IN, Pin.PULL_UP)    # cambia canal
btn_pwr = Pin(11, Pin.IN, Pin.PULL_UP)    # cambia potencia (la del ACK)
led_ok  = Pin(21, Pin.OUT)                # mensaje completo recibido
led_err = Pin(22, Pin.OUT)                # paquete fuera de secuencia

buf = b""
expect = 0
rx_ok = 0
rx_err = 0
last_text = ""


def pressed(pin):
    if pin.value() == 0:
        time.sleep_ms(30)
        if pin.value() == 0:
            while pin.value() == 0:
                time.sleep_ms(10)
            return True
    return False


def show():
    oled.fill(0)
    oled.text("RX Canal %d" % radio.channel, 0, 0)
    oled.text("%d MHz" % radio.freq_mhz, 0, 10)
    oled.text("%s %d dBm" % (RATES[radio.rate], POWER_DBM[radio.power]), 0, 20)
    oled.text(last_text[0:16], 0, 30)
    oled.text(last_text[16:32], 0, 40)
    oled.text("OK:%d ERR:%d" % (rx_ok, rx_err), 0, 50)
    oled.show()


def handle(pkt):
    """Reensambla el mensaje. Devuelve el texto completo o None."""
    global buf, expect, rx_err
    idx, seq, total, n = pkt[0], pkt[1], pkt[2], pkt[3]
    if n > CHUNK or total == 0 or seq >= total:
        rx_err += 1
        return None
    data = pkt[4:4 + n]
    if seq == 0:
        buf, expect = data, 1
    elif seq == expect:
        buf += data
        expect += 1
    else:                                   # se perdió un fragmento
        buf, expect = b"", 0
        rx_err += 1
        return None
    if seq == total - 1:
        expect = 0
        try:
            return buf.decode()
        except Exception:
            rx_err += 1
            return None
    return None


# ---------- Mensaje de inicio ----------
oled.fill(0)
oled.text("Lab Comunicacion", 0, 8)
oled.text("Digital Inalamb.", 0, 20)
oled.text("GFSK - NRF24L01", 0, 32)
oled.text("Receptor", 0, 48)
oled.show()
print("Receptor listo | canal", radio.channel, "|",
      RATES[radio.rate], "|", POWER_DBM[radio.power], "dBm")
time.sleep(2)

radio.start_listening()
show()

# ---------- Bucle principal ----------
while True:
    if pressed(btn_ch):
        radio.stop_listening()
        rb = radio.set_channel((radio.channel + CH_STEP) % 126)
        radio.start_listening()
        print("RF_CH =", rb)
        show()

    if pressed(btn_pwr):
        radio.stop_listening()
        radio.set_power((radio.power + 1) % 4)
        radio.start_listening()
        show()

    if radio.any():
        pkt = radio.recv()
        err_antes = rx_err
        text = handle(pkt)
        if text is not None:
            rx_ok += 1
            last_text = text
            print("Recibido:", text)
            led_ok.on()
            show()
            time.sleep_ms(100)
            led_ok.off()
        elif rx_err != err_antes:
            led_err.on()
            show()
            time.sleep_ms(100)
            led_err.off()

    time.sleep_ms(2)
