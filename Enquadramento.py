from Subcamada import Subcamada
from crc import CRC16
import time

FLAG = 0x7E
ESC = 0x7D
XOR = 0x20


class Enquadramento(Subcamada):

    OCIOSO = 0
    START = 1
    RX = 2
    ESCAPE = 3

    def __init__(self, porta_serial, tout=15, mtu=1024):
        super().__init__(porta_serial, tout)

        self.dev = porta_serial
        self.estado = self.OCIOSO
        self.buffer = bytearray()
        self.mtu = mtu

    def handle(self):
        byte = self.dev.read(1)

        if not byte:
            return

        b = byte[0]

        if self.estado == self.OCIOSO:

            if b == FLAG:
                self.buffer.clear()
                self.estado = self.START
                self.reload_timeout()

        elif self.estado == self.START:

            if b == FLAG:
                return

            self.buffer.clear()

            if b == ESC:
                self.estado = self.ESCAPE
            else:
                self.buffer.append(b)
                self.estado = self.RX

            self.reload_timeout()

        elif self.estado == self.RX:

            if b == FLAG:

                if len(self.buffer) < 3:
                    self.estado = self.OCIOSO
                    self.buffer.clear()
                    return

                crc = CRC16(self.buffer)

                if crc.check_crc():
                    dados = self.buffer[:-2]

                    if self.upper:
                        self.upper.recebe(bytes(dados))
                else:
                    print("Erro de CRC - quadro descartado")

                self.estado = self.OCIOSO
                self.buffer.clear()
                return

            elif b == ESC:
                self.estado = self.ESCAPE
                self.reload_timeout()
                return

            else:
                self.buffer.append(b)

                if len(self.buffer) > self.mtu:
                    print("Erro: quadro excedeu MTU")
                    self.estado = self.OCIOSO
                    self.buffer.clear()
                    return

                self.reload_timeout()

        elif self.estado == self.ESCAPE:

            if b == FLAG:
                print("Erro de escape - quadro descartado")
                self.estado = self.OCIOSO
                self.buffer.clear()
                return

            self.buffer.append(b ^ XOR)

            if len(self.buffer) > self.mtu:
                print("Erro: quadro excedeu MTU")
                self.estado = self.OCIOSO
                self.buffer.clear()
                return

            self.estado = self.RX
            self.reload_timeout()

    def handle_timeout(self):
        if self.estado != self.OCIOSO:
            print("Timeout no enquadramento em", time.time())

        self.estado = self.OCIOSO
        self.buffer.clear()
        self.reload_timeout()

    def envia(self, dados: bytes):

        crc = CRC16(dados)
        dados_crc = crc.gen_crc()

        quadro = bytearray()
        quadro.append(FLAG)

        for b in dados_crc:

            if b == FLAG or b == ESC:
                quadro.append(ESC)
                quadro.append(b ^ XOR)
            else:
                quadro.append(b)

        quadro.append(FLAG)

        self.dev.write(bytes(quadro))