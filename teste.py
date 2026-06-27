#!/usr/bin/python3

import sys
import poller

from serial import Serial

from Aplicacao import Aplicacao
from Enquadramento import Enquadramento
from Arq import ARQ
from Sessao import Sessao


TimeoutEnq = 15
TimeoutARQ = 5
TimeoutSessao = 10

ID_SESSAO = 30


if len(sys.argv) != 3:
    print(
        f'Uso: {sys.argv[0]} <porta_serial> <iniciador|passivo>'
    )
    sys.exit(1)


porta = Serial(
    sys.argv[1],
    baudrate=115200,
    timeout=0.1
)

papel = sys.argv[2].lower()

if papel not in ('iniciador', 'passivo'):
    print("O papel deve ser 'iniciador' ou 'passivo'")
    sys.exit(1)

iniciador = (papel == 'iniciador')


enq = Enquadramento(
    porta,
    TimeoutEnq
)

arq = ARQ(
    ID_SESSAO,
    None,
    TimeoutARQ
)

sessao = Sessao(
    iniciador,
    ID_SESSAO,
    None,
    TimeoutSessao
)

app = Aplicacao()


#
# monta a pilha
#
enq.conecta(arq)
arq.conecta(sessao)
sessao.conecta(app)


sched = poller.Poller()

sched.adiciona(enq)
sched.adiciona(arq)
sched.adiciona(sessao)
sched.adiciona(app)


print(f'Porta serial : {sys.argv[1]}')
print(f'Papel        : {papel}')
print(f'Sessão       : {ID_SESSAO}')

sched.despache()