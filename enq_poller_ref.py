#!/usr/bin/python3

from poller import Poller, Callback
import serial
import sys

# ------------------------
# CONFIG
# ------------------------
PORTA = '/dev/pts/4'
BAUD = 9600
MAX_LEN = 128

FLAG = b'~'
ESC = b'}'

# Serial NÃO bloqueante
ser = serial.Serial(PORTA, BAUD, timeout=0)
ser.reset_input_buffer()
ser.reset_output_buffer()

# ------------------------
# FUNÇÃO DE ESCAPE
# ------------------------
def aplicar_escape(msg_bytes):
    resultado = b''

    for b in msg_bytes:
        byte = bytes([b])

        if byte == FLAG:
            resultado += ESC + FLAG
        elif byte == ESC:
            resultado += ESC + ESC
        else:
            resultado += byte

    return resultado


# ------------------------
# CALLBACK SERIAL (RECEPÇÃO)
# ------------------------
class SerialCallback(Callback):
    def __init__(self, ser):
        super().__init__(ser, timeout=10)

        # Estados da MEF
        self.OCIOSO = 0
        self.START = 1
        self.RX = 2
        self.ESCAPE = 3

        self.estado = self.OCIOSO
        self.buffer = b''

    def handle(self):
        byte = self.fd.read(1)

        if not byte:
            return

        if self.estado == self.OCIOSO:
            if byte == FLAG:
                self.estado = self.START

        elif self.estado == self.START:
            if byte == FLAG:
                return  # ignora FLAG duplicada

            elif byte == ESC:
                self.estado = self.ESCAPE
                self.buffer = b''

            else:
                self.buffer = byte
                self.estado = self.RX

        elif self.estado == self.RX:
            if byte == FLAG:
                print("\nRecebido:", self.buffer.decode(errors='ignore'))
                self.estado = self.OCIOSO

            elif byte == ESC:
                self.estado = self.ESCAPE

            else:
                if len(self.buffer) < MAX_LEN:
                    self.buffer += byte
                else:
                    print("Erro: mensagem excedeu limite")
                    self.estado = self.OCIOSO

        elif self.estado == self.ESCAPE:
            if len(self.buffer) < MAX_LEN:
                self.buffer += bytes([byte[0] ^ 0x20])
            else:
                print("Erro: mensagem excedeu limite")

            self.estado = self.RX

    def handle_timeout(self):
        print("Timeout: resetando recepção")
        self.estado = self.OCIOSO
        self.buffer = b''


# ------------------------
# CALLBACK INPUT (ENVIO)
# ------------------------
class InputCallback(Callback):
    def __init__(self, ser):
        super().__init__(sys.stdin)
        self.ser = ser

    def handle(self):
        msg = sys.stdin.readline().strip()

        if not msg:
            return

        if len(msg) > MAX_LEN:
            print("Mensagem muito longa!")
            return

        dados = msg.encode()
        dados_esc = aplicar_escape(dados)

        quadro = FLAG + dados_esc + FLAG
        self.ser.write(quadro)

    def handle_timeout(self):
        pass


# ------------------------
# MAIN
# ------------------------
def main():
    poller = Poller()

    poller.adiciona(SerialCallback(ser))
    poller.adiciona(InputCallback(ser))

    print("Sistema pronto. Digite mensagens:")

    poller.despache()


if __name__ == "__main__":
    main()