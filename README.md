# Comunicación digital inalámbrica (parte 4.1) — NRF24L01 + Raspberry Pi Pico 2W

Laboratorio de **Comunicaciones Digitales** · Programa de Ingeniería en Telecomunicaciones · Universidad Militar Nueva Granada 
· Periodo 2026-2

**Autores:** Harol Felipe Riveros Sierra (1401660) · Salome Bohórquez Blanco (1401654)

**Docente:** Ing. José de Jesús Rugeles Uribe

---

## Descripción

Sistema de comunicación inalámbrica punto a punto en la banda ISM de 2,4 GHz con dos **Raspberry Pi Pico 2W** (un transmisor y un receptor), cada una con un módulo **NRF24L01** controlado por **SPI** y una pantalla **OLED SSD1306** por I²C.

La parte 4.1 de la guía consiste en conectar un **analizador lógico** al transmisor y, con **Logic 2**, capturar y decodificar tres operaciones SPI sobre el NRF24L01:

1. **Lectura de un registro** (`R_REGISTER` sobre `RF_SETUP`).
2. **Escritura del registro `RF_CH`** para cambiar el canal de radiofrecuencia (`W_REGISTER`).
3. **Transferencia del contenido de un paquete** al transceptor (`W_TX_PAYLOAD`).

Para cada captura se registraron el comando SPI, los bytes transmitidos y recibidos, las señales de control (CSN, SCK) y los tiempos de la transferencia. Además se verificó el efecto de cambiar canal y potencia sobre el enlace real.

## Contenido del repositorio

```
parte 4.1/
├── main_tx.py          # Firmware del transmisor (guardar como main.py en la Pico 1)
├── main_rx.py          # Firmware del receptor (guardar como main.py en la Pico 2)
├── nrf24.py            # Driver mínimo del NRF24L01 (copiar en ambas Pico)
├── taabla e estudiante 1.csv   # Exportación de Logic 2 de la captura del mensaje "Estudiante 1"
├── 9 INFORME COMUNICACION DIGITAL ( HAROL RIVEROS - SALOME BOHORQUEZ ).pdf   # Informe final
└── *.png / *.jpeg      # Capturas de Logic 2, consolas y fotos del montaje
```

## Hardware

| Cantidad | Elemento |
|---|---|
| 2 | Raspberry Pi Pico 2W |
| 2 | Módulo NRF24L01 |
| 2 | Pantalla OLED SSD1306 128x64 (I²C) |
| 1 | Analizador lógico de 8 canales y 24 MHz (usado con Logic 2) |
| 3 por Pico | Pulsadores (canal, potencia y, solo en TX, envío) |
| 2 por Pico | LED (OK y error) con resistencia de 220–330 Ω |

## Conexiones

El montaje es idéntico en transmisor y receptor.

**NRF24L01 ↔ Pico 2W**

| NRF24L01 | Pico 2W | Pin físico |
|---|---|---|
| VCC | 3V3(OUT) | 36 |
| GND | GND | 38 |
| CE | GP20 | 26 |
| CSN | GP17 | 22 |
| SCK | GP18 | 24 |
| MOSI | GP19 | 25 |
| MISO | GP16 | 21 |
| IRQ | sin conectar | — |

**OLED ↔ Pico 2W (I²C0)**

| OLED | Pico 2W | Pin físico |
|---|---|---|
| VCC | 3V3(OUT) | 36 |
| GND | GND | 38 |
| SDA | GP4 | 6 |
| SCL | GP5 | 7 |

**Pulsadores y LED**

| Función | GPIO | Pin físico | Dónde |
|---|---|---|---|
| Selección de canal | GP10 | 14 | TX y RX |
| Selección de potencia | GP11 | 15 | TX y RX |
| Envío de mensaje | GP12 | 16 | Solo TX |
| LED OK | GP21 | — | TX y RX |
| LED error | GP22 | — | TX y RX |

**Analizador lógico (solo en el transmisor)**

| Canal del analizador | Canal en Logic 2 | Señal | GPIO | Pin físico |
|---|---|---|---|---|
| CH1 | Canal 0 | CSN | GP17 | 22 |
| CH2 | Canal 1 | SCK | GP18 | 24 |
| CH3 | Canal 2 | MOSI | GP19 | 25 |
| CH4 | Canal 3 | MISO | GP16 | 21 |
| CH5 | Canal 4 | CE | GP20 | 26 |
| GND | — | Tierra | GND | 23 |

<p>
  <img src="montaje%20de%20TX.jpeg" width="32%" alt="Montaje del transmisor">
  <img src="montaje%20de%20RX.jpeg" width="32%" alt="Montaje del receptor">
  <img src="Montaje%20de%20TX%20con%20el%20analizador%20logico.jpeg" width="32%" alt="Transmisor con el analizador lógico">
</p>

## Software y puesta en marcha

1. Cargar **MicroPython** en las dos Raspberry Pi Pico 2W.
2. Desde **Thonny** (*Herramientas → Administrar paquetes*) instalar la biblioteca de la OLED (`micropython-ssd1306`) en cada Pico.
3. Copiar `nrf24.py` a **las dos** Pico.
4. Guardar `main_tx.py` como `main.py` en la Pico del **transmisor** y `main_rx.py` como `main.py` en la del **receptor**.
5. Alimentar ambas placas. La OLED muestra el mensaje de inicio y luego canal, frecuencia, velocidad y potencia.

### Configuración por defecto

| Parámetro | Valor |
|---|---|
| Canal | 40 (2440 MHz; frecuencia = 2400 + canal MHz) |
| Velocidad | 1 Mbps |
| Potencia | 0 dBm |
| Auto-ACK | Activado (reintentos: 15, espera 1500 µs) |
| Payload | 32 bytes fijos |
| Dirección | `UMNG1` (igual en TX y RX) |
| SPI | 1 MHz, modo 0 |
| I²C (OLED) | 400 kHz |

Los parámetros `CHANNEL`, `POWER`, `RATE`, `AUTO_ACK` y `CHUNK` se cambian al inicio de `main_tx.py` y `main_rx.py`. **Deben coincidir en ambas placas.**

## Funcionamiento

### Controles

| Pulsador | Transmisor | Receptor |
|---|---|---|
| GP10 | Sube el canal en pasos de 4 (módulo 126) | Igual: debe seguir al transmisor |
| GP11 | Cambia la potencia (-18, -12, -6, 0 dBm) | Cambia la potencia (la usada para el ACK) |
| GP12 | Envía el mensaje actual y pasa al siguiente | — |

### Formato del paquete

Cada mensaje se fragmenta en paquetes de 32 bytes con una cabecera de 4 bytes:

| Byte 0 | Byte 1 | Byte 2 | Byte 3 | Bytes 4–31 |
|---|---|---|---|---|
| Índice del mensaje | N.º de fragmento (`seq`) | Total de fragmentos | Largo de datos | Datos (máx. 28) + relleno `0x00` |

Por ejemplo, "Estudiante 1" se envía con la cabecera `00 00 01 0C`, seguida de los 12 caracteres y 16 bytes `0x00` de relleno. Los mensajes de más de 28 bytes se dividen en dos paquetes. El receptor reensambla los fragmentos y marca error si llega uno fuera de secuencia.

### Indicadores

- **LED verde:** envío confirmado (TX) o mensaje completo recibido (RX).
- **LED rojo:** envío fallido (TX) o paquete fuera de secuencia (RX).
- **OLED:** estado, mensaje actual y, en el receptor, contadores `OK` / `ERR`.
- **Consola de Thonny:** registra cada cambio de canal, potencia y envío.

## Pruebas y resultados

### 1. Lectura de registro (`RF_SETUP`)

- Comando `0x06` (`R_REGISTER` + dirección `0x06`) y un byte nulo para generar el reloj.
- El primer byte recibido por MISO es siempre `STATUS` (`0x0E`); el segundo es el contenido del registro (`0x00`: -18 dBm, 1 Mbps).
- Duración de la transacción: ≈ 29 µs con CSN en bajo.

![Lectura de registro](Lectura%20de%20registro%20enviando%20estudiante%201.png)

### 2. Escritura de `RF_CH` (cambio de canal 40 → 44)

- Comando `0x25` (`W_REGISTER` + dirección `0x05`) seguido del valor `0x2C` (44 decimal): el enlace pasa de 2440 MHz a 2444 MHz.
- CSN en bajo ≈ 40 µs.
- Cada byte dura ≈ 7,583 µs, lo que equivale a un SCK cercano a 1,05 MHz (nominal: 1 MHz).

![Cambio de canal de 40 a 44](cambio%20de%20canal%20de%2040%20a%2044.png)

### 3. Cambio de canal solo en el transmisor (fallo esperado)

- Con el TX en el canal 44 y el RX en el 40 no hay enlace.
- `STATUS` pasa a `0x1E`: se activa `MAX_RT` al agotarse los reintentos. Después se limpian las banderas escribiendo `0x27 0x70`.
- El fallo se confirma en la OLED (`FALLO`), el LED rojo y la consola del transmisor.

<p>
  <img src="cambio%20e%20canal%20unicamente%20en%20Tx.png" width="48%" alt="Cambio de canal solo en TX">
  <img src="Env%C3%ADo%20fallido%20se%20cambio%20el%20canla%20solo%20en%20el%20TX.png" width="48%" alt="Envío fallido por canales distintos">
</p>
<p>
  <img src="pantalla%20de%20Tx%20informando%20que%20hubo%20un%20fallo%20en%20el%20envio%20del%20mensaje.jpeg" width="32%" alt="OLED del TX con FALLO">
  <img src="Tx%20cuando%20el%20mensaje%20fall%C3%B3.jpeg" width="32%" alt="TX cuando el mensaje falló">
  <img src="Consola%20dde%20Tx%20cuando%20no%20sse%20envia%20el%20mensaje.jpeg" width="32%" alt="Consola del TX con FALLO">
</p>

### 4. Transferencia de un paquete (`W_TX_PAYLOAD`)

- Comando `0xA0` seguido de los 32 bytes del payload: **33 bytes** en total.
- Mensaje "Estudiante 1": cabecera `00 00 01 0C`, caracteres del mensaje y relleno `0x00`. La captura completa está en `taabla e estudiante 1.csv`.
- Cada byte dura ≈ 7,583 µs, con ≈ 9,5 µs entre bytes.
- CSN permanece en bajo ≈ 356,1 µs, y pasan ≈ 31 µs entre la bajada de CSN y el primer pulso de SCK.
- "Estudiante 2" mantiene la misma estructura; solo cambian la cabecera y los datos.

![Transferencia Estudiante 1](Lectura%20de%20registro%20enviando%20estudiante%201.png)
![Transferencia Estudiante 2](cambio%20de%20potencia%20estuddiante%202.png)

### 5. Mensaje largo en dos paquetes

- El mensaje `abcdefghijklmnopqrstuvwxyz0123456789` (36 caracteres) supera los 28 bytes útiles y se divide en dos paquetes.
- Paquete 0: `abcdefghijklmnopqrstuvwxyz01`. Paquete 1: `23456789`.
- El segundo paquete es más corto porque lleva menos datos útiles; el payload se completa igualmente hasta 32 bytes.

<p>
  <img src="Mensaje%20largo%20en%20dos%20paquetes.png" width="48%" alt="Primer paquete">
  <img src="Mensaje%20largo%20en%20dos%20paquetes_2.png" width="48%" alt="Segundo paquete">
</p>

### 6. Cambio de potencia y validación de la recepción

- Escritura `0x26 0x00` sobre `RF_SETUP`: potencia de -18 dBm a 1 Mbps.
- Tras el cambio, el receptor recibe correctamente "Estudiante 1", "Estudiante 2", el alfabeto en mayúsculas y el mensaje de alfabeto + dígitos, con el LED verde encendido y los mensajes en la consola.

<p>
  <img src="cambio%20de%20potena%20a%20-18bddm%20en%20tx.png" width="32%" alt="Potencia -18 dBm en TX">
  <img src="cambio%20de%20potencia%20e%200%20a%20-18dbm%20en%20rx.png" width="32%" alt="Potencia -18 dBm en RX">
  <img src="Rx%20cuando%20el%20mensaje%20llega%20sin%20error.jpeg" width="32%" alt="RX sin errores">
</p>
<p>
  <img src="consola%20de%20Rx%20con%20los%20mensajes%20recibidos.jpeg" width="60%" alt="Consola del receptor con los mensajes recibidos">
</p>

## Resumen de transacciones SPI observadas

| Operación | Comando | Bytes MOSI | Primer byte MISO | CSN en bajo |
|---|---|---|---|---|
| Leer `RF_SETUP` | `0x06` | `06 00` | `STATUS` = `0x0E` | ≈ 29 µs |
| Escribir `RF_CH` | `0x25` | `25 2C` | `STATUS` = `0x0E` | ≈ 40 µs |
| Limpiar banderas `STATUS` | `0x27` | `27 70` | `STATUS` = `0x1E` (tras `MAX_RT`) | — |
| Escribir `RF_SETUP` | `0x26` | `26 00` | `STATUS` | — |
| Cargar paquete | `0xA0` | `A0` + 32 bytes | `STATUS` | ≈ 356,1 µs |

## Conclusiones

- Se conectó correctamente el NRF24L01 a la Pico 2W por SPI y se adquirieron las señales CSN, SCK, MOSI y MISO con el analizador lógico.
- Se identificaron los comandos `R_REGISTER`, `W_REGISTER` y `W_TX_PAYLOAD`, y se comprobó que el primer byte que devuelve el módulo es siempre `STATUS`.
- El cambio de canal y de potencia se vio directamente en el bus SPI y se comprobó en el enlace real. Con canales distintos en TX y RX se activa `MAX_RT` y el envío falla.
- Los tiempos medidos (≈ 7,583 µs por byte, SCK ≈ 1,05 MHz) concuerdan con el baudrate configurado de 1 MHz.

## Informe

El análisis completo, con marco teórico y referencias, está en el archivo PDF `9 INFORME COMUNICACION DIGITAL ( HAROL RIVEROS - SALOME BOHORQUEZ ).pdf`.

## Referencias

1. Wikipedia. *Serial Peripheral Interface*. https://es.wikipedia.org/wiki/Serial_Peripheral_Interface
2. Sigma Electrónica. *NRF24L01*. https://www.sigmaelectronica.net/producto/nrf24l01/
3. MK Electrónica. *Analizador lógico LA2408*. https://mkelectronica.com/producto/analizador-logico-la2408/
4. Sigma Electrónica. *RPI PICO 2W*. http://sigmaelectronica.net/producto/rpi-pico-2w/
5. Rugeles, J. *Comunicación digital inalámbrica* [Guía de laboratorio]. Universidad Militar Nueva Granada.
