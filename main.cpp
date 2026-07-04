#include "MidiClientUtil.h"
#include "DataConfig.h"
#include <iostream>

DataConfig loadConfigData()
{
    DataConfig dataConfig = DataConfig{};
    dataConfig.telnetHost = "localhost";
    dataConfig.telnetPort = "5500";

    auto dataConfigMidiInput = DataConfigMidiInput{};
    dataConfigMidiInput.midiInputIdx = 0;
    dataConfigMidiInput.midiInputName = "Launch Control XL";

    DataConfigFromMidiToTelnet dcfmttThrottle{};
    dcfmttThrottle.fromStart = 0;
    dcfmttThrottle.fromEnd = 127;
    dcfmttThrottle.toStart = 0;
    dcfmttThrottle.toEnd = 1;
    dcfmttThrottle.midiMsgType = MidiMsgType::CONTROL_CHANGE;
    dcfmttThrottle.midiChannel = -1;
    dcfmttThrottle.notePitchOrCcChannel = 77;
    dcfmttThrottle.setCmd = "/controls/engines/engine[0]/throttle";
    dataConfigMidiInput.dataConfigFromMidiToTelnets.push_back(std::move(dcfmttThrottle));

    DataConfigFromMidiToTelnet dcfmttRudder{};
    dcfmttRudder.fromStart = 0;
    dcfmttRudder.fromEnd = 127;
    dcfmttRudder.toStart = 1;
    dcfmttRudder.toEnd = -1;
    dcfmttRudder.midiMsgType = MidiMsgType::CONTROL_CHANGE;
    dcfmttRudder.midiChannel = -1;
    dcfmttRudder.notePitchOrCcChannel = 78;
    dcfmttRudder.setCmd = "/controls/flight/rudder";
    dataConfigMidiInput.dataConfigFromMidiToTelnets.push_back(std::move(dcfmttRudder));

    DataConfigFromMidiToTelnet dcfmttAileron{};
    dcfmttAileron.fromStart = 0;
    dcfmttAileron.fromEnd = 127;
    dcfmttAileron.toStart = 1;
    dcfmttAileron.toEnd = -1;
    dcfmttAileron.midiMsgType = MidiMsgType::CONTROL_CHANGE;
    dcfmttAileron.midiChannel = -1;
    dcfmttAileron.notePitchOrCcChannel = 79;
    dcfmttAileron.setCmd = "/controls/flight/aileron";
    dataConfigMidiInput.dataConfigFromMidiToTelnets.push_back(std::move(dcfmttAileron));

    DataConfigFromMidiToTelnet dcfmttElevator{};
    dcfmttElevator.fromStart = 0;
    dcfmttElevator.fromEnd = 127;
    dcfmttElevator.toStart = -1;
    dcfmttElevator.toEnd = 1;
    dcfmttElevator.midiMsgType = MidiMsgType::CONTROL_CHANGE;
    dcfmttElevator.midiChannel = -1;
    dcfmttElevator.notePitchOrCcChannel = 80;
    dcfmttElevator.setCmd = "/controls/flight/elevator";
    dataConfigMidiInput.dataConfigFromMidiToTelnets.push_back(std::move(dcfmttElevator));

    DataConfigFromMidiToTelnet dcfmttMixure{};
    dcfmttMixure.fromStart = 0;
    dcfmttMixure.fromEnd = 127;
    dcfmttMixure.toStart = 0;
    dcfmttMixure.toEnd = 1;
    dcfmttMixure.midiMsgType = MidiMsgType::CONTROL_CHANGE;
    dcfmttMixure.midiChannel = -1;
    dcfmttMixure.notePitchOrCcChannel = 84;
    dcfmttMixure.setCmd = "/controls/engines/current-engine/mixture";
    dataConfigMidiInput.dataConfigFromMidiToTelnets.push_back(std::move(dcfmttMixure));

    dataConfig.dataConfigMidiInputs.push_back(std::move(dataConfigMidiInput));

    DataConfigPullerFgKey pullerThrottle;
    pullerThrottle.fgKetPath = "/controls/engines/engine[0]/throttle";
    dataConfig.dataConfigPullerFgKeys.push_back(std::move(pullerThrottle));

    DataConfigPullerFgKey pullerRudder;
    pullerRudder.fgKetPath = "/controls/flight/rudder";
    dataConfig.dataConfigPullerFgKeys.push_back(std::move(pullerRudder));
    return dataConfig;
}

int runFlightGearClient()
{
    auto midiItf = getMidiClientItf();

    midiItf->setDataConfig(loadConfigData());

    std::cout << "in ports:\n";
    for (const auto &itm : midiItf->getInPorts())
    {
        std::cout << " " << itm << "\n";
    }
    std::cout << "out ports:\n";
    for (const auto &itm : midiItf->getOutPorts())
    {
        std::cout << " " << itm << "\n";
    }
    std::cout << "\n";

    bool terminalMode = false;
    try
    {
        midiItf->startMidiClient();
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
                    midiItf->startMidiClient();
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
                        midiItf->startMidiClient();
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

int main(int argc, char *argv[])
{
    auto midiItf = getMidiClientItf();
    midiItf->testSendNotesOn();
    return 0;
}
