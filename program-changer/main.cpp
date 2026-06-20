#include <iostream>
#include <string>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netdb.h>

class TelnetClient {
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

    // Background thread loop
    void readServer() {
        char buffer;

        while (is_running) {
            // Read exactly 1 byte. This blocks until FlightGear sends *anything*
            ssize_t bytes = recv(sock_fd, &buffer, 1, 0);
            
            if (bytes <= 0) {
                std::cerr << "\n[DEBUG] Socket error or closed. Bytes: " << bytes << "\n";                
                is_running = false;
                break; 
            }

            // 1. Force absolute instant terminal echoing (Bypasses stream lockups)
            //std::cout << buffer;
            //std::cout.flush();

            {
                std::lock_guard<std::mutex> lock(data_mutex);
                if (expecting_data) {
                    accumulated_line += buffer;

                    // CHECK Condition A: FlightGear is in data mode and returned a clean line
                    bool found_newline = (accumulated_line.find('\n') != std::string::npos);
                    

                    if (found_newline ) {
                        
                        // Clean up and strip verbose properties/prompts from the value string
                        while (!accumulated_line.empty() && 
                            (accumulated_line.back() == '\n' || 
                            accumulated_line.back() == '\r' )) {
                            accumulated_line.pop_back();
                        }
                                                
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


    void start() {
        if (is_running) return; 
        is_running = true;
        receiver_thread = std::thread(&TelnetClient::readServer, this);

        // FIX: Wait a moment for FlightGear's initial welcoming burst to finish arriving
        std::cerr << "[INIT] Waiting for FlightGear login/telnet negotiation bytes...\n";
        std::this_thread::sleep_for(std::chrono::milliseconds(400));

        // Put FlightGear into data mode safely now that the stream is quiet
        std::cerr << "[INIT] Sending 'data\\r\\n' mode command to FlightGear...\n";
        std::string mode_cmd = "data\r\n";
        send(sock_fd, mode_cmd.c_str(), mode_cmd.length(), 0);

        // Give FlightGear a brief window to process the transition internally
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

public:
    bool isRunning() const{
        return is_running;
    }

    ~TelnetClient() {
        stop();
    }

    bool openSocket(const std::string &host, const std::string port ){
        stop();
        struct addrinfo hints{}, *res;
        hints.ai_family = AF_INET; 
        hints.ai_socktype = SOCK_STREAM;

        if (getaddrinfo(host.c_str(), port.c_str(), &hints, &res) != 0) {
            std::cerr << "Failed to resolve hostname\n";
            return false;
        }

        sock_fd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
        if (sock_fd < 0) {
            std::cerr << "Socket creation failed\n";
            freeaddrinfo(res);
            return false;
        }

        if (connect(sock_fd, res->ai_addr, res->ai_addrlen) < 0) {
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




    // Sends a property read request and blocks with a built-in safety timeout
    std::string getValue(const std::string& path) {
        std::unique_lock<std::mutex> lock(data_mutex);
        
        response_ready = false;
        expecting_data = true;
        latest_response.clear();
        accumulated_line.clear();

        std::string cmd = "get " + path + "\r\n";
        //std::cerr << "[TX] " << cmd;
        send(sock_fd, cmd.c_str(), cmd.length(), 0);

        // Fail-safe wait limit: blocks for up to 3 seconds max
        auto timeout = std::chrono::seconds(3);
        bool success = data_cv.wait_for(lock, timeout, [this]() { return response_ready; });

        if (!success) {
            std::cerr << "[TIMEOUT ERROR] FlightGear did not reply with a newline within 3 seconds.\n";
            expecting_data = false; // Reset lock state
            return "ERROR_TIMEOUT";
        }

        return latest_response;
    }

    // Sets a property value (Note: 'set' requests do not trigger back-and-forth replies)
    void setValue(const std::string& path, const std::string& val) {        
        std::string cmd = "set " + path + " " + val + "\r\n";
        send(sock_fd, cmd.c_str(), cmd.length(), 0);
    }

    void stop() {
        is_running = false;
        if (sock_fd != -1) {
            close(sock_fd);
            sock_fd = -1;
        }
        if (receiver_thread.joinable()) {
            receiver_thread.join();
        }
    }
};

int main(int argc, char* argv[]) {


    std::string host = "localhost";
    std::string port = "5500";



    TelnetClient client;
    
    if (!client.openSocket(host,port)){
        return 0;
    }

    // Give FlightGear a brief window to parse and transition to data mode internally
    std::this_thread::sleep_for(std::chrono::milliseconds(250));

    /*
    for (float i=0;i<=100;i++){
        std::cout << "\n[get RESULT] "<< std::to_string(0.01* i)<< " " << client.getValue("/controls/engines/engine[0]/throttle") << "\n\n";
    }
    */
    
    for (float i=0;i<=100;i++){
        client.setValue("/controls/engines/engine[0]/throttle",std::to_string(0.01* i) );
        std::cout << "\n[set RESULT] " << std::to_string(0.01* i) << "\n\n";
    }
    

    std::string userInput;

    std::getline(std::cin, userInput); 


    client.stop();
    return 0;
}
