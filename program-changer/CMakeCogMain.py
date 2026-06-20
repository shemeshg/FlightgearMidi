from jinja2 import Environment, FileSystemLoader
import os

template_dict = {
           "APP_VER": "0.1.0"
           }



environment = Environment(loader=FileSystemLoader("."))
template = environment.get_template("CMakeCogMain.j2")


content = template.render(
    template_dict
)

def getCmake():   
    return content
#print(getCmake())