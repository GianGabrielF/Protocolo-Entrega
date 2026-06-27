class Quadro:

    DATA = 0b000
    KA   = 0b011
    CR   = 0b100
    CC   = 0b101
    DR   = 0b110
    DC   = 0b111

    def __init__(self, tipo=DATA, seq=0, sessao=0, dados=b'', ack=False):
        self.tipo = tipo
        self.seq = seq
        self.sessao = sessao
        self.dados = dados
        self.ack = ack

    @property
    def controle(self):
        ctrl = 0

        if self.ack:
            ctrl |= 0x80

        ctrl |= (self.seq & 1) << 3
        ctrl |= self.tipo & 0x07

        return ctrl

    def to_bytes(self):
        return bytes([
            self.controle,
            self.sessao
        ]) + self.dados

    @staticmethod
    def from_bytes(buffer):
        if len(buffer) < 2:
            raise ValueError("Quadro inválido")

        controle = buffer[0]
        sessao = buffer[1]
        dados = buffer[2:]

        ack = (controle & 0x80) != 0
        seq = (controle >> 3) & 0x01
        tipo = controle & 0x07

        return Quadro(
            tipo=tipo,
            seq=seq,
            sessao=sessao,
            dados=dados,
            ack=ack
        )

    def __repr__(self):
        return (
            f"Quadro("
            f"ack={self.ack}, "
            f"tipo={self.tipo}, "
            f"seq={self.seq}, "
            f"sessao={self.sessao}, "
            f"dados={self.dados!r}"
            f")"
        )