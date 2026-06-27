from Subcamada import Subcamada
from Quadro import Quadro


class Sessao(Subcamada):

    DESCONECTADO = 0
    AGUARDANDO_CC = 1
    CONECTADO = 2
    AGUARDANDO_DC = 3

    def __init__(
        self,
        iniciador,
        id_sessao,
        fd=None,
        tout=10
    ):

        super().__init__(fd, tout)

        self.iniciador = iniciador
        self.id_sessao = id_sessao

        if iniciador:
            self.estado = self.DESCONECTADO
        else:
            self.estado = self.DESCONECTADO

        self.disable_timeout()

    def handle(self):
        pass

    def conecta(self, uplayer):
        self.upper = uplayer
        uplayer.lower = self

        #
        # iniciador abre conexão automaticamente
        #
        if self.iniciador:
            self.abrir()

    def abrir(self):

        if self.estado != self.DESCONECTADO:
            return

        print("Sessão: enviando CR")

        quadro = Quadro(
            tipo=Quadro.CR,
            seq=0,
            sessao=self.id_sessao
        )

        self.lower.envia(quadro)

        self.estado = self.AGUARDANDO_CC

        self.reload_timeout()
        self.enable_timeout()

    def fechar(self):

        if self.estado != self.CONECTADO:
            return

        print("Sessão: enviando DR")

        quadro = Quadro(
            tipo=Quadro.DR,
            seq=0,
            sessao=self.id_sessao
        )

        self.lower.envia(quadro)

        self.estado = self.AGUARDANDO_DC

        self.reload_timeout()
        self.enable_timeout()

    def envia(self, dados: bytes):

        if self.estado != self.CONECTADO:
            print("Sessão não estabelecida")
            return

        quadro = Quadro(
            tipo=Quadro.DATA,
            seq=0,
            sessao=self.id_sessao,
            dados=bytes([0x00]) + dados
        )

        self.lower.envia(quadro)

    def recebe(self, quadro: Quadro):

        if quadro.sessao != self.id_sessao:
            return

        #
        # RECEPÇÃO DE CR
        #
        if quadro.tipo == Quadro.DATA:

            if self.estado != self.CONECTADO:
                return

            dados = quadro.dados

            if len(dados) > 0:
                dados = dados[1:]

            if self.upper:
                self.upper.recebe(dados)

            return

        #
        # RECEPÇÃO DE CC
        #
        if quadro.tipo == Quadro.CC:

            print("Sessão: CC recebido")

            if self.estado == self.AGUARDANDO_CC:

                self.estado = self.CONECTADO

                self.disable_timeout()

                print("Sessão estabelecida")

            return

        #
        # RECEPÇÃO DE DR
        #
        if quadro.tipo == Quadro.DR:

            print("Sessão: DR recebido")

            resposta = Quadro(
                tipo=Quadro.DC,
                seq=0,
                sessao=self.id_sessao
            )

            self.lower.envia(resposta)

            self.estado = self.DESCONECTADO

            self.disable_timeout()

            print("Sessão encerrada")

            return

        #
        # RECEPÇÃO DE DC
        #
        if quadro.tipo == Quadro.DC:

            print("Sessão: DC recebido")

            if self.estado == self.AGUARDANDO_DC:

                self.estado = self.DESCONECTADO

                self.disable_timeout()

                print("Sessão encerrada")

            return

        #
        # RECEPÇÃO DE DADOS
        #
        if quadro.tipo == Quadro.DATA:

            if self.estado != self.CONECTADO:
                return

            if self.upper:
                self.upper.recebe(quadro.dados)

    def handle_timeout(self):

        #
        # retransmissão do CR
        #
        if self.estado == self.AGUARDANDO_CC:

            print("Timeout Sessão - reenviando CR")

            quadro = Quadro(
                tipo=Quadro.CR,
                seq=0,
                sessao=self.id_sessao
            )

            self.lower.envia(quadro)

            self.reload_timeout()

        #
        # retransmissão do DR
        #
        elif self.estado == self.AGUARDANDO_DC:

            print("Timeout Sessão - reenviando DR")

            quadro = Quadro(
                tipo=Quadro.DR,
                seq=0,
                sessao=self.id_sessao
            )

            self.lower.envia(quadro)

            self.reload_timeout()