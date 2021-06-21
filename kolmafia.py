import re
import zipfile
import jnius_config
KOLMAFIA_PATH = "./kolmafia.jar"
jnius_config.set_classpath(KOLMAFIA_PATH)
# import requests
from jnius import autoclass, cast
import json


archive = zipfile.ZipFile(KOLMAFIA_PATH)
JAVA_PATTERN = "(net\/sourceforge\/kolmafia.*\/([^\$]*))\.class"
ByteArrayOutputStream = autoclass("java.io.ByteArrayOutputStream")
ByteArrayInputStream = autoclass("java.io.ByteArrayInputStream")
PrintStream = autoclass("java.io.PrintStream")
String = autoclass("java.lang.String")
List = autoclass("java.util.List")
RETURNED_PATTERN = "(?:Returned: |)(.*)\r\n"

class MafiaAbort(Exception):
    pass

class CLICommand:
    def __init__(self, command):
        self.command = command
        self.text = ""
        self.status = None
        self.value = ""
        
    def set_text(self, text):
        self.text = text
        match = re.search(RETURNED_PATTERN, text)
        #aggressive attribution of the return value of a command based on the output stream of mafia
        if match:
            self.value = match.group(1)
        
    def set_status(self, status):
        self.status = status
        
    def __str__(self):
        return self.text
    
    def __repr__(self):
        return str(self)


class KoLmafia:
    def __init__(self):
        self.PWD = None
        self.classes = {}
        for file in archive.filelist:
            filename = file.orig_filename
            match = re.search(JAVA_PATTERN, filename)
            if match:
                self.classes[match.group(2)] = match.group(1)
            
    def launch_gui(self):
        self.KoLmafia.main(["--GUI"])
        
    def login(self, username, password = None):
        password = password or km.KoLmafia.getSaveState(username)
        km.LoginRequest(username, password).run()
        
    def launch_relay_server(self):
        if not km.RelayServer.isRunning():
            km.RelayServer.startThread()
        
    def cli(self, s, raise_if_aborted = True):
        command = CLICommand(s)
        ostream = ByteArrayOutputStream()
        ostream = cast("java.io.OutputStream", ostream)
        out = PrintStream(ostream)
        km.RequestLogger.openCustom(out)
        km.KoLmafiaCLI.DEFAULT_SHELL.executeLine(s)
        km.RequestLogger.closeCustom()
        command.set_text(ostream.toString())
        command.set_status(km.NamespaceInterpreter.getContinueValue())
        if raise_if_aborted and not command.status:
            raise MafiaAbort
        return command
    
    def ash(self, s):
        #not sure if this processing is necessary
        s = s.strip()
        if s[-1] != ";":
            s += ";"
        s += "\n"
        script = ByteArrayInputStream(String(s).getBytes())
        runtime = km.AshRuntime()
        runtime.validate(None, script)
        return runtime.execute("main", None).toString() #add type-specific functionality here
            
    def get_property(self, key):
        return self.ash(f"""get_property("{key}")""")

    def set_property(self, key, value):
        value = str(value)
        return self.ash(f"""set_property("{key}","{value}")""")
    
    
    def __getattr__(self, key):
        if key in self.classes:
            attr = autoclass(self.classes.get(key))
            self.__setattr__(key, attr)
            return attr
        else:
            raise NotImplementedError

                            
km = KoLmafia()