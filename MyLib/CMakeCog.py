from jinja2 import Environment, FileSystemLoader
import os

import ImportScript
from GenHpp import GenHpp

from pathlib import Path

template_dict = {
           "APP_VER": "0.1.0",
           "BIN_NAME": "MyLib",
           "FETCH_CONTENT" : [{
                "LIB":  "libremidi",
                "GIT_REPOSITORY" : "https://github.com/celtera/libremidi" ,
                "GIT_TAG" : "master",
                "target_link": "libremidi"
           },
           {
                "LIB":  "sigslot",
                "GIT_REPOSITORY" : "https://github.com/palacaze/sigslot" ,
                "GIT_TAG" : "master",
                "target_link": "Pal::Sigslot"
           },
           {
                "LIB":  "cpr",
                "GIT_REPOSITORY" : "https://github.com/libcpr/cpr.git" ,
                "GIT_TAG" : "1.10.5",
                "target_link": "cpr::cpr"
           },
           {
                "LIB":  "json",
                "GIT_REPOSITORY" : "https://github.com/nlohmann/json" ,
                "GIT_TAG" : "master",
                "target_link": "nlohmann_json::nlohmann_json"
           },                     
           
           ]

           }

hppFolders = ["hpp"]
genHpp = GenHpp(template_dict["BIN_NAME"])
genHpp.makeDirectories = [f"${{CMAKE_CURRENT_BINARY_DIR}}/{item}" for item in hppFolders]
genHpp.hppGenFilesTemplates = ["${CMAKE_SOURCE_DIR}/scripts/hppTemplates.txt"]
genHpp.hppGenFilesGlobes = [f"{item}/*.hpp" for item in hppFolders]
genHpp.parseHppPyPath = "${CMAKE_SOURCE_DIR}/scripts/parseHpp.py"    
template_dict["HPP_SCMAKE_SCRIPT"] = genHpp.getStr()
template_dict["HPP_CPP_FILES"] = genHpp.getDefineFiles("${CMAKE_CURRENT_BINARY_DIR}/")
template_dict["HPP_GEN_LINK"] = genHpp.add_dependencies()
template_dict["HPP_INCLUDE_PUBLIC_DIR"] = genHpp.makeDirectories

hppGenFilesGlobesStr = []
for globStr in  genHpp.hppGenFilesGlobes:
    hppGenFilesGlobesStr.extend(sorted(["${CMAKE_CURRENT_SOURCE_DIR}/" + str(p) for p in Path(globStr).parent.glob(Path(globStr).name )]))
template_dict["HPP_ORG_HPP_FILES"] = hppGenFilesGlobesStr

environment = Environment(loader=FileSystemLoader("."))
template = environment.get_template("CMakeCog.j2")


content = template.render(
    template_dict
)

def getCmake():   
    return content
#print(getCmake())