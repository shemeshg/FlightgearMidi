#include "TelnetClient.h"
#include "MidiClientUtil.h"
#include <iostream>

int testTelnet()
{

    std::string host = "localhost";
    std::string port = "5500";
    
    TelnetClient client;

    if (!client.openSocket(host, port))
    {
        return 0;
    }

    // Give FlightGear a brief window to parse and transition to data mode internally
    std::this_thread::sleep_for(std::chrono::milliseconds(250));

    /*
    for (float i=0;i<=100;i++){
        std::cout << "\n[get RESULT] "<< std::to_string(0.01* i)<< " " << client.getValue("/controls/engines/engine[0]/throttle") << "\n\n";
    }
    */

    for (float i = 0; i <= 100; i++)
    {
        client.setValue("/controls/engines/engine[0]/throttle", std::to_string(0.01 * i));
        std::cout << "\n[set RESULT] " << std::to_string(0.01 * i) << "\n\n";
    }

    std::string userInput;

    std::getline(std::cin, userInput);

    client.stop();

    return 0;
}

int main(int argc, char *argv[])
{

    auto midiItf = getMidiClientItf();
    midiItf->testMidi();


    return 0;
}
