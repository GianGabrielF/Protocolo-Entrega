from poller import Callback


class Subcamada(Callback):

    def __init__(self, fd, tout):
        Callback.__init__(self, fd, tout)
        self.lower = None
        self.upper = None

    def conecta(self, uplayer):
        self.upper = uplayer
        uplayer.lower = self

    def envia(self, dados: bytes):
        raise NotImplementedError("abstrato")

    def recebe(self, dados: bytes):
        raise NotImplementedError("abstrato")