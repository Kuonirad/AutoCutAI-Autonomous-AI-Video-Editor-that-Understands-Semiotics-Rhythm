// bb-extract.cpp  –  basic-block hit matrix exporter
// g++ -O2 bb-extract.cpp -lz -o bb-extract
// ./bb-extract run1.json run2.json … > bb.csv

#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main(int argc, char* argv[])
{
    if (argc < 2) { std::cerr << "usage: bb-extract run1.json run2.json … > bb.csv\n"; return 1; }

    std::vector<std::string>    header;      // ordered block names
    std::vector<std::vector<int>> matrix;    // one row per run

    for (int i = 1; i < argc; ++i) {
        std::ifstream in(argv[i]);
        if (!in) { std::perror(argv[i]); return 1; }
        json j;  in >> j;

        std::map<std::string,int> hits;      // name -> count for this run
        for (auto &f : j["data"][0]["functions"])
            for (auto &r : f["regions"])
                if (r["kind"] == "block") {
                    std::string name = f["name"].get<std::string>() + ":" +
                                       std::to_string(r["line_start"].get<int>());
                    hits[name] = r["count"].get<int>();
                }

        if (header.empty()) {
            for (auto const& [name, val] : hits) header.push_back(name);
            std::cout << "run";
            for (auto const& h : header)
                std::cout << "," << h;
            std::cout << "\n";
        }

        matrix.emplace_back();
        for (auto &h : header) matrix.back().push_back(hits[h]);
    }

    for (size_t i = 0; i < matrix.size(); ++i) {
        std::cout << "run" << i+1;
        for (size_t k = 0; k < matrix[i].size(); ++k)
            std::cout << "," << matrix[i][k];
        std::cout << "\n";
    }
    return 0;
}
