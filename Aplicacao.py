from Subcamada import Subcamada
import sys

class Aplicacao(Subcamada):
    
    def __init__(self):
        Subcamada.__init__(self, sys.stdin,10)
  
    def recebe(self, dados: bytes):
        print('RX:', dados.decode(errors='ignore'))

    def handle(self):
        linha = sys.stdin.readline()

        if not linha:
            return  # evita enviar vazio / EOF

        dados = linha.rstrip('\n').encode('utf8')

        if self.lower:
            self.lower.envia(dados)