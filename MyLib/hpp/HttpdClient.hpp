//-define-file body hpp/HttpdClient.cpp
//-define-file header hpp/HttpdClient.h

//-only-file header //-
#pragma once
#include <string>
#include <unordered_map>

//-only-file body //-
//- #include "HttpdClient.h"
#include <cpr/cpr.h>
#include <iostream>
#include <nlohmann/json.hpp>

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
    void updateQueryMapVals(std::unordered_map<std::string, std::string> &requestUrls)
    //-only-file body
    {
        std::vector<cpr::AsyncWrapper<cpr::Response>> futures;
        futures.reserve(requestUrls.size());

        // Launch async requests
        for (const auto &pair : requestUrls)
        {
            futures.emplace_back(
                cpr::GetAsync(
                    cpr::Url{getUrl(pair.first)},
                    cpr::Header{{"Content-Type", "application/json"}}));
        }

        // Collect results
        auto f_it = futures.begin();
        for (auto &pair : requestUrls)
        {
            cpr::Response r = f_it->get();
            ++f_it;

            if (!r.error)
            {
                auto json = nlohmann::json::parse(r.text);
                pair.second = json["value"].dump(); // always string
            }
        }
    }

    //-only-file header
private:
    std::string hostName = "localhost";
    std::string hostPort = "8800";

    //-only-file header
};