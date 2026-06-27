//-define-file body hpp/TelnetClient.cpp
//-define-file header hpp/TelnetClient.h
//-only-file body //-
//- #include "TelnetClient.h"
#include <iostream>
#include <chrono>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>
#include <regex>
//-only-file header //-
#pragma once
#include <string>
#include <thread>
#include <mutex>
#include <condition_variable>

//-only-file header
//-var {PRE} "TelnetClient::"
class TelnetClient
{

public:
    std::function<void()> on_disconnect;

    //- {fn}
    bool isRunning() const
    //-only-file body
    {
        return is_running;
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
        struct addrinfo hints{}, *res;
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_STREAM;

        if (getaddrinfo(host.c_str(), port.c_str(), &hints, &res) != 0)
        {
            std::cerr << "Failed to resolve hostname\n";
            return false;
        }

        sock_fd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
        if (sock_fd < 0)
        {
            std::cerr << "Socket creation failed\n";
            freeaddrinfo(res);
            return false;
        }

        if (connect(sock_fd, res->ai_addr, res->ai_addrlen) < 0)
        {
            std::cerr << "Connection failed\n";
            close(sock_fd);
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
        // std::cerr << "[TX] " << cmd;
        send(sock_fd, cmd.c_str(), cmd.length(), 0);

        // Fail-safe wait limit: blocks for up to 3 seconds max
        auto timeout = std::chrono::seconds(3);
        bool success = data_cv.wait_for(lock, timeout, [this]()
                                        { return response_ready; });

        if (!success)
        {
            std::cerr << "[TIMEOUT ERROR] FlightGear did not reply with a newline within 3 seconds.\n";
            expecting_data = false; // Reset lock state
            return "ERROR_TIMEOUT";
        }

        return latest_response;
    }

    //- {fn}
    std::string getValue(const std::string &path)
    //-only-file body
    {
        return getCmd("get " + path );
    }

    //- {fn}
    void setValue(const std::string &path, const std::string &val)
    //-only-file body
    {
        std::string cmd = "set " + path + " " + val + "\r\n";
        send(sock_fd, cmd.c_str(), cmd.length(), 0);
    }

    //- {fn}
    void stop()
    //-only-file body
    {
        is_running = false;
        std::cout << "In func stop()\n";
        if (sock_fd != -1)
        {
            close(sock_fd);
            sock_fd = -1;
            std::cout << "In func stop() fd closed\n";
        }
        if (receiver_thread.joinable() && receiver_thread.get_id() != std::this_thread::get_id())
        {
            receiver_thread.join();
        }
    }

    //-only-file header
private:
    int sock_fd = -1;

    std::thread receiver_thread;
    std::atomic<bool> is_running{false};

    // Synchronization variables
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
            // Read exactly 1 byte. This blocks until FlightGear sends *anything*
            ssize_t bytes = recv(sock_fd, &buffer, 1, 0);

            if (bytes <= 0)
            {
                std::cerr << "\n[DEBUG] Socket error or closed. Bytes: " << bytes << "\n";
                // is_running = false;
                stop();
                if (on_disconnect)
                    on_disconnect();
                break;
            }

            // 1. Force absolute instant terminal echoing (Bypasses stream lockups)
            // std::cout << buffer;
            // std::cout.flush();

            {
                std::lock_guard<std::mutex> lock(data_mutex);
                if (expecting_data)
                {
                    accumulated_line += buffer;

                    // CHECK Condition A: FlightGear is in data mode and returned a clean line
                    //bool found_newline = (accumulated_line.find('\n') != std::string::npos);
                    std::string lastLine;

                    // Find last newline
                    std::size_t pos = accumulated_line.find_last_of("\r\n");

                    if (pos == std::string::npos) {
                        lastLine = accumulated_line;            // only one line
                    } else {
                        lastLine = accumulated_line.substr(pos + 1);
                    }
                    
                    // Now check the pattern
                    bool found_prompt_no_data_mode =
                        !lastLine.empty() &&
                        lastLine.front() == '/' &&
                        lastLine.back()  == '>';

                    
                    if (found_prompt_no_data_mode) {
                        latest_response = accumulated_line;
                        response_ready = true;
                        expecting_data = false;
                        accumulated_line.clear();

                        data_cv.notify_one();

                    }
                }
            }
        }
        is_running = false;
    }

    //- {fn}
    void start()
    //-only-file body
    {
        if (is_running)
            return;
        is_running = true;
        receiver_thread = std::thread(&TelnetClient::readServer, this);

        // FIX: Wait a moment for FlightGear's initial welcoming burst to finish arriving
        std::cerr << "[INIT] Waiting for FlightGear login/telnet negotiation bytes...\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(400));

        /*
        // Put FlightGear into data mode safely now that the stream is quiet
        std::cerr << "[INIT] Sending 'data\\r\\n' mode command to FlightGear...\n";
        std::string mode_cmd = "data\r\n";
        send(sock_fd, mode_cmd.c_str(), mode_cmd.length(), 0);

        // Give FlightGear a brief window to process the transition internally
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
        */
    }

    //- {fn}
    std::string trim_regex(const std::string &s)
    //-only-file body
    {
        return std::regex_replace(s, std::regex(R"(^\s+|\s+$)"), "");
    }

    //-only-file header
};