//-define-file body hpp/TelnetClient.cpp
//-define-file header hpp/TelnetClient.h

//-only-file body //-
//- #include "TelnetClient.h"
#include <iostream>
#include <chrono>
#include <regex>

#if defined(_WIN32)
    #define CLOSESOCK closesocket
#else
    #define CLOSESOCK close
#endif

//-only-file header //-
#pragma once
#include <string>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>

#include <boost/signals2.hpp>

#if defined(_WIN32)
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #pragma comment(lib, "ws2_32.lib")
    typedef long ssize_t;   // <-- FIX 1: Windows lacks ssize_t
#else
    #include <sys/socket.h>
    #include <arpa/inet.h>
    #include <unistd.h>
    #include <netdb.h>
#endif

//-only-file header
//-var {PRE} "TelnetClient::"
class TelnetClient
{

public:
    boost::signals2::signal<void(bool)> sigIsRunningChanged;

    //- {fn}
    bool isRunning() const
    //-only-file body
    {
        return is_running;
    }

    //- {fn}
    bool getIsTerminalDebugMode() const
    //-only-file body
    {
        return isTerminalDebugMode;
    }

    //- {fn}
    void setIsTerminalDebugMode(bool bl)
    //-only-file body
    {
        isTerminalDebugMode = bl; 
    }

    //- {function} 0 0
    ~TelnetClient()
    //-only-file body
    {
        stop();
    }

    //- {fn}
    bool openSocket(const std::string &host, const std::string port)
    //-only-file body
    {
        stop();

#if defined(_WIN32)
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2,2), &wsaData) != 0)
        {
            std::cerr << "WSAStartup failed\n";
            return false;
        }
#endif

        struct addrinfo hints{}, *res;
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_STREAM;

        if (getaddrinfo(host.c_str(), port.c_str(), &hints, &res) != 0)
        {
            std::cerr << "Failed to resolve hostname\n";
            return false;
        }

        sock_fd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);

#if defined(_WIN32)
        if (sock_fd == INVALID_SOCKET)
#else
        if (sock_fd < 0)
#endif
        {
            std::cerr << "Socket creation failed\n";
            freeaddrinfo(res);
            return false;
        }

        if (connect(sock_fd, res->ai_addr, res->ai_addrlen) < 0)
        {
            std::cerr << "Connection failed\n";
            CLOSESOCK(sock_fd);
#if defined(_WIN32)
            sock_fd = INVALID_SOCKET;
            WSACleanup();
#else
            sock_fd = -1;
#endif
            freeaddrinfo(res);
            return false;
        }
        freeaddrinfo(res);
        std::cout << "[Connected to " << host << ":" << port << "]\n";
        start();
        return true;
    }

    //- {fn}
    std::string getCmd(const std::string &rawCmd)
    //-only-file body
    {
        std::unique_lock<std::mutex> lock(data_mutex);

        response_ready = false;
        expecting_data = true;
        latest_response.clear();
        accumulated_line.clear();

        std::string cmd = trim_regex(rawCmd) + "\r\n";
        send(sock_fd, cmd.c_str(), static_cast<int>(cmd.length()), 0);  

        auto timeout = std::chrono::seconds(3);
        bool success = data_cv.wait_for(lock, timeout, [this]()
                                        { return response_ready; });

        if (!success)
        {
            std::cerr << "[TIMEOUT ERROR] FlightGear did not reply with a newline within 3 seconds.\n";
            expecting_data = false;
            return "ERROR_TIMEOUT";
        }

        return latest_response;
    }

    //- {fn}
    std::string getValue(const std::string &path)
    //-only-file body
    {
        return getCmd("get " + path);
    }

     //- {fn}
    void sendTerminalRaw(std::string cmd) 
    //-only-file body
    {
        std::string s = cmd + "\r\n";
        send(sock_fd, s.c_str(), static_cast<int>(s.length()), 0);  // <-- FIX 2
    }

    //- {fn}
    void setValue(const std::string &path, const std::string &val)
    //-only-file body
    {
        std::string cmd = "set " + path + " " + val + "\r\n";
        send(sock_fd, cmd.c_str(), static_cast<int>(cmd.length()), 0);  // <-- FIX 2
    }

    //- {fn}
    void stop()
    //-only-file body
    {
        setsRunning(false);
        std::cout << "In func stop()\n";
        if (
#if defined(_WIN32)
            sock_fd != INVALID_SOCKET
#else
            sock_fd != -1
#endif
        )
        {
            CLOSESOCK(sock_fd);
#if defined(_WIN32)
            sock_fd = INVALID_SOCKET;
            WSACleanup();
#else
            sock_fd = -1;
#endif
            std::cout << "In func stop() fd closed\n";
        }
        if (receiver_thread.joinable() && receiver_thread.get_id() != std::this_thread::get_id())
        {
            receiver_thread.join();
        }
    }

    //-only-file header
private:
    bool isTerminalDebugMode = false;

#if defined(_WIN32)
    SOCKET sock_fd = INVALID_SOCKET;
#else
    int sock_fd = -1;
#endif

    std::thread receiver_thread;
    std::atomic<bool> is_running{false};

    std::mutex data_mutex;
    std::condition_variable data_cv;
    std::string latest_response;
    std::string accumulated_line;
    bool response_ready = false;
    bool expecting_data = false;

    //- {fn}
    void readServer()
    //-only-file body
    {
        char buffer;

        while (is_running)
        {
            ssize_t bytes = recv(sock_fd, &buffer, 1, 0);  // <-- FIX 1 makes this valid

            if (bytes <= 0)
            {
                std::cerr << "\n[DEBUG] Socket error or closed. Bytes: " << bytes << "\n";
                stop();
                break;
            }

            if (isTerminalDebugMode) {
                std::cout << buffer;
                std::cout.flush();
            }
            
            {
                std::lock_guard<std::mutex> lock(data_mutex);
                if (expecting_data)
                {
                    accumulated_line += buffer;

                    std::string lastLine;

                    std::size_t pos = accumulated_line.find_last_of("\r\n");

                    if (pos == std::string::npos)
                    {
                        lastLine = accumulated_line;
                    }
                    else
                    {
                        lastLine = accumulated_line.substr(pos + 1);
                    }

                    bool found_prompt_no_data_mode =
                        !lastLine.empty() &&
                        lastLine.front() == '/' &&
                        lastLine.back() == '>';

                    bool found_prompt_data_mode = !accumulated_line.empty() &&
                               (accumulated_line.back() == '\n' ||
                                accumulated_line.back() == '\r');

                    if (found_prompt_no_data_mode || found_prompt_data_mode)
                    {
                        latest_response = accumulated_line;
                        response_ready = true;
                        expecting_data = false;
                        accumulated_line.clear();

                        data_cv.notify_one();
                    }
                }
            }
        }
        setsRunning(false);
    }

    //- {fn}
    void start()
    //-only-file body
    {
        if (is_running)
            return;
        setsRunning(true);

        receiver_thread = std::thread(&TelnetClient::readServer, this);

        std::cerr << "[INIT] Waiting for FlightGear login/telnet negotiation bytes...\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(400));

        std::cerr << "[INIT] Sending 'data\\r\\n' mode command to FlightGear...\n";
        std::string mode_cmd = "data\r\n";
        send(sock_fd, mode_cmd.c_str(), static_cast<int>(mode_cmd.length()), 0);  // <-- FIX 2

        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        
    }

    //- {fn}
    std::string trim_regex(const std::string &s)
    //-only-file body
    {
        return std::regex_replace(s, std::regex(R"(^\s+|\s+$)"), "");
    }

    //-only-file header
    void setsRunning(bool bl)
    {
        if (bl != is_running)
        {
            is_running = bl;
            sigIsRunningChanged(is_running);
        }
    }
};
