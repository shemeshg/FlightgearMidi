from typing import List
import glob
from pathlib import Path
import re
import hashlib
from string import Template

class GenHpp:
    execJobId: str
    makeDirectories: List[str] = []
    hppGenFilesGlobes: List[str] = []
    hppGenFilesTemplates: List[str] = []
    parseHppPyPath: str = ""
    exeName: str
    def __init__(self, exeName: str):        
        hash_object = hashlib.sha256(exeName.encode())
        self.execJobId: str = "runScript_" +  hash_object.hexdigest()
        self.exeName: str = exeName

    def add_dependencies(self) -> str:
        t: Template = Template("""
if(GEN_HPP)
  add_dependencies(${exeName} ${execJobId})
endif()
        """)
        return t.substitute(exeName = self.exeName, 
                            execJobId = self.execJobId)

    def get_string_parts(self, line: str, with_quotes: bool = False) -> List[str]:
        if with_quotes:
            pattern: re.Pattern[str] = re.compile(r'(\".*?\"|\S+<.*?>|\S+\s*\*\s*|\S+)')
        else:
            pattern: re.Pattern[str] = re.compile(r'\"(.*?)\"|(\S+<.*?>|\S+\s*\*\s*|\S+)')

        matches: List[str] = pattern.findall(line)

        if with_quotes:
            parts: List[str] = [match for match in matches]
        else:
            parts: List[str] = [match[0] or match[1] for match in matches]

        return parts

    def getDefineFiles(self, preAppend: str = "") -> List[str]:
        defFiles: List[str] = []
        for globStr in self.hppGenFilesGlobes:
            globStr = globStr.replace('${CMAKE_CURRENT_SOURCE_DIR}/','')
            globStr = globStr.replace('"','')
            files: List[str] = [str(p) for p in glob.glob(globStr)]
            for file in files:
                with open(file, 'r') as f:                    
                    for line in f:
                        line = line.strip()
                        if line.startswith("//-define-file"):                            
                            defFiles.append(preAppend + self.get_string_parts(line)[2])
        return defFiles

    def getStr(self) -> str:
        makeDirsStr: str = ""
        if len(self.makeDirectories) > 0:
            makeDirsStrT: Template = Template("""make_directory(${items})""")
            makeDirsStr += "\n".join( [makeDirsStrT.substitute(items = m)  for m in self.makeDirectories] )


        hppGenFilesTemplatesStr: str = ""
        if len(self.hppGenFilesTemplates) > 0:
            hppGenFilesTemplatesStr = " ".join(self.hppGenFilesTemplates)

        
        hppGenFilesGlobesStr: List[str] = []
        for globStr in  self.hppGenFilesGlobes:      
            hppGenFilesGlobesStr.extend(sorted(["${CMAKE_CURRENT_SOURCE_DIR}/" + str(p) for p in Path(globStr).parent.glob(Path(globStr).name )]))

        t: Template = Template("""
SET(GEN_HPP TRUE)
if(GEN_HPP)
    find_package(Python3 REQUIRED COMPONENTS Interpreter)
                               
    ${makeDirsStr}


    set(HPP_GEN_FILES
        ${hppGenFilesTemplatesStr}
        ${hppGenFilesGlobesStr}
    )
    add_custom_target(${execJobId} ALL
        COMMAND ${Python3_EXECUTABLE} ${parseHppPyPath} ${HPP_GEN_FILES}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Running parseHpp shell script")

    # Run a shell script before everything else
    execute_process(
        COMMAND ${Python3_EXECUTABLE} ${parseHppPyPath} ${HPP_GEN_FILES}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        RESULT_VARIABLE result
    )

    # Check the result of the script execution
    if(NOT result EQUAL 0)
        message(FATAL_ERROR "Script execution failed with result: ${result}")
    endif()

    # Continue with the rest of your CMake configuration
endif()
                     """)
        return t.safe_substitute(makeDirsStr = makeDirsStr, 
                                 hppGenFilesTemplatesStr = hppGenFilesTemplatesStr,
                                 hppGenFilesGlobesStr = "\n".join(hppGenFilesGlobesStr),
                                 execJobId = self.execJobId,
                                 parseHppPyPath = self.parseHppPyPath)