# main_tx.py -> guardar como main.py en la Pico 1 (TRANSMISOR)
# Necesita en la Pico: nrf24.py y ssd1306.py
from machine import Pin, SPI, I2C
import time
import ssd1306
from nrf24 import NRF24, RATES, POWER_DBM

# ---------- Configuración ----------
CHANNEL  = 40      # canal inicial (frecuencia = 2400 + canal MHz)
POWER    = 3       # 0:-18  1:-12  2:-6  3:0 dBm
RATE     = 1       # 0:250 kbps  1:1 Mbps  2:2 Mbps
CH_STEP  = 4       # cuánto sube el canal con cada pulsación
AUTO_ACK = True    # False = sin ACK ni reintentos (útil para medir BER)
CHUNK    = 28      # bytes de datos por paquete (4 bytes de cabecera)

MESSAGES = [
    "Estudiante 1",
    "Estudiante 2",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "abcdefghijklmnopqrstuvwxyz0123456789",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
]

# ---------- Hardware ----------
i2c  = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)          # cambiar a 32 si es 128x32
spi  = SPI(0, baudrate=1_000_000, polarity=0, phase=0,
           sck=Pin(18), mosi=Pin(19), miso=Pin(16))
radio = NRF24(spi, csn=17, ce=20, channel=CHANNEL, power=POWER,
              rate=RATE, auto_ack=AUTO_ACK)

btn_ch   = Pin(10, Pin.IN, Pin.PULL_UP)   # cambia canal
btn_pwr  = Pin(11, Pin.IN, Pin.PULL_UP)   # cambia potencia
btn_send = Pin(12, Pin.IN, Pin.PULL_UP)   # envía el mensaje actual
led_ok   = Pin(21, Pin.OUT)               # envío confirmado
led_err  = Pin(22, Pin.OUT)               # envío fallido

msg_idx = 0


def pressed(pin):
    """Antirrebote: True una vez por pulsación (al soltar)."""
    if pin.value() == 0:
        time.sleep_ms(30)
        if pin.value() == 0:
            while pin.value() == 0:
                time.sleep_ms(10)
            return True
        
    return False


def show(status=""):
    oled.fill(0)
    oled.text("TX Canal %d" % radio.channel, 0, 0)
    oled.text("%d MHz" % radio.freq_mhz, 0, 10)
    oled.text("%s %d dBm" % (RATES[radio.rate], POWER_DBM[radio.power]), 0, 20)
    oled.text("Msg %d/%d" % (msg_idx + 1, len(MESSAGES)), 0, 30)
    oled.text(MESSAGES[msg_idx][:16], 0, 40)
    oled.text(status, 0, 50)
    oled.show()


def send_message(idx):
    """Fragmenta el mensaje en paquetes: [id, seq, total, largo] + datos."""
    msg = MESSAGES[idx].encode()
    chunks = [msg[i:i + CHUNK] for i in range(0, len(msg), CHUNK)] or [b""]
    for seq, c in enumerate(chunks):
        pkt = bytes([idx, seq, len(chunks), len(c)]) + c
        if not radio.send(pkt):
            return False
    return True


# ---------- Mensaje de inicio ----------
oled.fill(0)
oled.text("Lab Comunicacion", 0, 8)
oled.text("Digital Inalamb.", 0, 20)
oled.text("GFSK - NRF24L01", 0, 32)
oled.text("Transmisor", 0, 48)
oled.show()
print("Transmisor listo | canal", radio.channel, "|",
      RATES[radio.rate], "|", POWER_DBM[radio.power], "dBm")
time.sleep(2)
show("Listo")

# ---------- Bucle principal ----------
while True:
    if pressed(btn_ch):
        ch = (radio.channel + CH_STEP) % 126
        rb = radio.set_channel(ch)
        print("RF_CH =", rb)
        show("Canal cambiado")

    if pressed(btn_pwr):
        rb = radio.set_power((radio.power + 1) % 4)
        print("RF_SETUP = 0x%02X" % rb)
        show("Potencia cambiada")

    if pressed(btn_send):
        show("Enviando...")
        ok = send_message(msg_idx)
        led = led_ok if ok else led_err
        led.on()
        time.sleep_ms(300)
        led.off()
        print("Msg", msg_idx, "OK" if ok else "FALLO")
        show("Enviado OK" if ok else "FALLO")
        msg_idx = (msg_idx + 1) % len(MESSAGES)

    time.sleep_ms(10)
