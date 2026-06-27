#include <iostream>
#include "Serial.h"
#include "Callback.h"
#include "poller.h"

using namespace std;

class CbSerial: public Callback {
private:
    Serial & porta;
public:
    CbSerial(Serial & porta): Callback(porta.get(), 0), porta(porta) {
        disable_timeout();
    }

    void handle() {
        auto msg = porta.read(128);
        // mostra na tela os caracteres recebidos
        cout.write(msg.data(), msg.size());
        cout << "==================================" << endl;
    }

    void handle_timeout() {

    }
};

int main(int argc, char * argv[]) {
    // cria um objeto Serial para acessar a porta serial indicada em argv[1],
    // com taxa de 9600 bps
    Serial rf(argv[1], B9600);

    Poller sched;
    CbSerial cb(rf);
    sched.adiciona(&cb);

    sched.despache();

    cout << endl;
}