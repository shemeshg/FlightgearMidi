from jinja2 import Environment, FileSystemLoader
import os

template_dict = {
           "APP_VER": "0.2.0",
           "PROGRAM_NAME": "program-changer",
           "add_subdirectory_lib": ["MyLib"],
           "add_subdirectory_header_only": ["FlightgearMidi"]
           }

template_dict["add_subdirectory_lib_target"] = [os.path.basename(path) for path in template_dict["add_subdirectory_lib"]]

environment = Environment(loader=FileSystemLoader("."))
template = environment.get_template("CMakeCogMain.j2")


content = template.render(
    template_dict
)

def getCmake():   
    return content
#print(getCmake())