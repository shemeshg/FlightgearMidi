from jinja2 import Environment, FileSystemLoader
import os

from CMakeCogMain import template_dict

environment = Environment(loader=FileSystemLoader("."))
template = environment.get_template("pyprojectCog.j2")


content = template.render(
    template_dict
)

def getText():   
    return content