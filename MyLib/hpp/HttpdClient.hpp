//-define-file body hpp/HttpdClient.cpp
//-define-file header hpp/HttpdClient.h

//-only-file header //-
#pragma once
#include <string>

//-only-file body //-
//- #include "HttpdClient.h"
#include <cpr/cpr.h>
#include <iostream>

//-only-file header
//-var {PRE} "HttpdClient::"
class HttpdClient
{
public:
    //- {function} 0 2
    const std::string getUrl(std::string key) const
    //-only-file body
    {
        while (!key.empty() && key.front() == '/')
            key.erase(0, 1);

        return "http://" + hostName + ":" + hostPort + "/json/" + key;
    }

    //- {fn}
    void testQuery(std::string requestUrl)
    //-only-file body
    {
        std::vector<cpr::AsyncWrapper<cpr::Response>> futures;
        futures.reserve(4);

        for (int i = 0; i < 4; ++i)
        {
            futures.emplace_back(
                cpr::GetAsync(
                    cpr::Url{requestUrl},
                    cpr::Header{{"Content-Type", "application/json"}}));

        }

        // Wait for all responses
        for (auto &f : futures)
        {
            cpr::Response r = f.get();

            if (r.error)
            {
                std::cerr << "Request failed: " << r.error.message << "\n";
                continue;
            }
            std::cout << r.text <<"\n";
            //auto json = nlohmann::json::parse(r.text);
            //std::cout << "Response JSON: " << json.dump(2) << "\n";
        }
    }

    //-only-file header
private:
    std::string hostName = "localhost";
    std::string hostPort = "8800";

    //-only-file header
};