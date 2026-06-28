#include "MidiClientUtil.h"
#include <iostream>


int main(int argc, char *argv[])
{
    std::unordered_map<std::string, bool> profiles = {
        {"c172p-fg1000-kap", false}
    };


    
    auto midiItf = getMidiClientItf();
    midiItf->getInPorts();
    midiItf->getOutPorts();
    bool terminalMode = false;
    try
    {
        midiItf->testMidi();
        std::string userInput;
        while (true)
        {
            if (midiItf->getIsTelnetRunning())
            {
                std::getline(std::cin, userInput);
                if (terminalMode)
                {
                }
                else
                {
                    std::cout << "\nConnected\nq=quit\nt=terminal mode on/off\n";
                }

                if (userInput == "q")
                {
                    break;
                }
                else if (userInput == "t")
                {
                    terminalMode = !terminalMode;
                    midiItf->setIsTerminalDebugMode(terminalMode);
                    if (terminalMode)
                    {
                        std::cout << "t - to exit terminal mode\n";
                    }
                }
                else if (terminalMode)
                {
                    midiItf->sendTerminalRaw(userInput);
                }
            }
            else
            {
                if (midiItf->getIsTelnetDisconnectedSignal())
                {
                    std::cout << "Try to Rrestart\n";
                    midiItf->testMidi();
                }
                else
                {
                    std::cout << "Not Connected\n r=restart q=quit\n";
                    std::getline(std::cin, userInput);
                    if (userInput == "q")
                    {
                        break;
                    }
                    else if (userInput == "r")
                    {
                        midiItf->testMidi();
                    }
                }
            }
        }
    }
    catch (const std::exception &e)
    {
        std::cerr << e.what() << '\n';
    }

    return 0;
}
