from Subcamada import Subcamada
from Quadro import Quadro


class ARQ(Subcamada):

    OCIOSO = 0
    ESPERA = 1

    def __init__(self, id_sessao, fd=None, tout=5, max_retries=3):
        super().__init__(fd, tout)

        self.id_sessao = id_sessao

        self.estado = self.OCIOSO

        # sequência de transmissão
        self.N = 0

        # sequência esperada na recepção
        self.M = 0

        # último quadro transmitido em bytes
        self.ultimo_quadro = None

        self.max_retries = max_retries
        self.retries = 0

        self.disable_timeout()

    def handle(self):
        pass

    def envia(self, quadro: Quadro):

        if self.estado != self.OCIOSO:
            print("ARQ ocupado aguardando ACK")
            return

        quadro.seq = self.N
        quadro.sessao = self.id_sessao
        quadro.ack = False

        raw = quadro.to_bytes()

        print("ARQ TX quadro:", quadro)
        print("ARQ TX bytes :", raw.hex(" "))

        self.ultimo_quadro = raw
        self.retries = 0

        self.lower.envia(raw)

        self.estado = self.ESPERA

        self.reload_timeout()
        self.enable_timeout()

    def recebe(self, dados: bytes):

        try:
            quadro = Quadro.from_bytes(dados)

            print("ARQ RX bytes:", dados.hex(" "))
            print("ARQ RX quadro:", quadro)

        except Exception as e:
            print("Erro ao interpretar quadro:", e)
            return

        if quadro.sessao != self.id_sessao:
            return

        #
        # ACK recebido
        #
        if quadro.ack:

            if self.estado == self.ESPERA and quadro.seq == self.N:

                self.N ^= 1

                self.estado = self.OCIOSO

                self.ultimo_quadro = None

                self.retries = 0

                self.disable_timeout()

            return

        #
        # DATA recebido com sequência esperada
        #
        if quadro.seq == self.M:

            ack = Quadro(
                seq=self.M,
                sessao=self.id_sessao,
                ack=True
            )

            self.lower.envia(
                ack.to_bytes()
            )

            if self.upper:
                self.upper.recebe(quadro)

            self.M ^= 1

        #
        # DATA duplicado
        #
        else:

            ack = Quadro(
                seq=quadro.seq,
                sessao=self.id_sessao,
                ack=True
            )

            self.lower.envia(
                ack.to_bytes()
            )

    def handle_timeout(self):

        if self.estado != self.ESPERA:
            return

        if self.retries >= self.max_retries:
            print("ARQ: limite de retransmissões atingido")

            self.estado = self.OCIOSO
            self.ultimo_quadro = None
            self.retries = 0
            self.disable_timeout()
            return

        print("Timeout ARQ - retransmitindo")

        if self.ultimo_quadro:
            self.lower.envia(self.ultimo_quadro)

        self.retries += 1
        self.reload_timeout()