
#!/usr/bin/env python3

import yaml
import sys
import os
import glob
import pandas as pd
from yaml.loader import SafeLoader


#Habrá que desarrollar también alguna herramientas de apoyoÇ:
##función para crear argumentos que sirvan de entrada a modArgFromDict

###ToDo: cambiar args y esas cosas de build-in a output normal con opción?
####Aquí hay clases que en rigor tienen que acabar en otro archivo.


class pipeConfig():
    def __init__(self, file, type_name = "type", pos_name = "pos", value_name = "value", flag_value = "flag", pos_value = "pos"):
        self.config = self.openConfig(file)
        self.pipes = self.getPipes()
        self.type_name = type_name
        self.pos_name = pos_name
        self.value_name = value_name
        self.flag_value = flag_value
        self.pos_value = pos_value
        self.type_values = [self.flag_value, self.pos_value]
        self.pipe_input_types = (set, list)

    def openConfig(self, file): #Ampliar para que admita, al menos, JSON.
        try:
            with open(file, "r") as f:
                self.config = yaml.load(f, Loader= SafeLoader)
                print(f"{f} open")
            return self.config
        except:
            print("Unable to load config file")
            sys.exit(0)

    def getPipes(self):
        self.pipes = [x for x in self.config.keys()]

    def buildArgs (self, flag = "--", pipe = {}): #ToDo: error management. Que devuelva el argumento tal cual!
        self.args = {}
        if pipe:
            if self.checkPipes(pipe):
                configDict = {key : value for key, value in self.config.items() if key in pipe}
            else:
                return None
        else:
            configDict = self.config

        for key, value in configDict.items():
            cmdBuilder = ""
            posDict = {}

            for arg, params in value.items():
                if params[self.type_name] == self.flag_value:
                    cmdBuilder += flag + str(arg).strip() + " " + str(params[self.value_name]).strip() + " "
                elif params[self.type_name] == self.pos_value:
                    posDict[params[self.pos_name]] = str(params[self.value_name] + " ")

            if posDict: #order positional arguments. Maybe independet funcion?
                posArg = ""
                idx_list = [x for x in posDict.keys()]
                idx_list.sort()
                for idx in idx_list:
                    posArg += str(posDict[idx])
                cmdBuilder = cmdBuilder + posArg
            self.args[key] = cmdBuilder.rstrip() #build the cmd
            
    def buildCMD(self): #Ojo, devuelve una lista. Se debería dar la opción de devolver un string!
        cmds = []
        for pipe in self.args.keys():
            cmd = f"{pipe} {self.args[pipe]}"
            cmds.append(cmd)
        return cmds

    def addArgFromDict(self, pipes, dict):
        ##validate dict : {arg: {type : flag | pos, pos = int, value = str | int}}¿Clase con método?
        if not isinstance(pipes, (set, list)):
            print("pipes arg must be set or list (set recommended)")
            return None
        for pipe in pipes: ##Comprobar que el argumento no existe ya!!!
            if dict.keys() in self.config[pipe].keys():
                print("Duplicate arg!!. For update arg, you must use modArgFromDict method!!")
                return None
            self.config[pipe].update(dict)
        
    def addArgManually(self, pipes, arg, type, value, pos = "", replace_pos = False):
        if type not in self.type_values:
            print("type argument only addmits the following values: flag, pos") ##Esto debería aplicarse con el validador de argumentos
            return None
        if not self.validatePipeInput(pipes) or not self.checkPipes(pipes):
            return None

        newArg = {arg : {self.type_name : type, self.value_name : value}}

        if type == self.pos_value: ##Check if pos have conflicts!! ¿Validate?
            if pos:
                newArg[arg].update({self.pos_name :  pos})
            else:
                print("pos arg must be specified. Please correct")
                return None
        for pipe in pipes:
            ##Check if positional argument just exist:
            for value in self.config[pipe].values():
                if value[self.type_name] == self.pos_value and pos:  #El problema es que hay que revisar posicion a posicion
                    if value[self.pos_name] == newArg[arg][self.pos_name] and not replace_pos:
                        print ("Conflict between positional args!!!")
                        return None
            self.config[pipe].update(newArg)

    def validatePipeInput(self, pipes):
        if isinstance (pipes, self.pipe_input_types):
            return True
        else:
            print("pipes arg must be set or list. (Set recommended)")
            return False

    def checkPipes(self, pipes): #¿Modificar esto para que devuelva un dict tipo {pipe: bool}
        if self.validatePipeInput(pipes):
            for pipe in pipes:
                if pipe in self.config.keys():
                    return True
                else:
                    print(f"pipeline {pipe} not in config file")
                    return False

    def modArgFromDict(self, pipes, dict):
        ##Estrucutra del dict: {arg1:{arg_type_dict}, arg2:  {arg_type_dict}}... Esta estructura debe validarse
        pass

    def modArgManually(self, pipes, arg, type = "", value = "", pos = ""):
        if type and type not in self.type_values:
            print(f"incorrect type value. Only {self.type_values} addmitted")
        if self.checkPipes(pipes):
            for pipe in pipes:
                argsModifier = { self.type_name: type, self.value_name : value, self.pos_value : pos }
                argsModifier = {key:value for key, value in argsModifier.items() if value}
                if arg in self.config[pipe].keys():
                    self.config[pipe][arg].update(argsModifier)
                else:
                    print(f"{arg} not in {pipe}") #El validador de argumentos tiene que pasar al final y eliminar las cosas que no cuadren.
            
    def checkArgs(self, pipes, arg): #Esto va a funcionar regular. En realdiad no tiene que ser de instancia
        if self.checkPipes(pipes):
            checker = True
            for pipe in pipes:
                if arg not in self.config[pipe].keys():
                    print(f"{arg} not in {pipe}")
                    checker = False
            return checker

    def validateConfig(self):
        for pipe, args in self.config.items():
            for key in args.keys():
                pass

    def validateArgs(self, dict): #Crear clase propia???? !No de instancia
        self.structure = {
            "type_name" :  self.type_name,
            "pos_name" : self.pos_name,
            "value_name" : self.value_name,
            "flag_value" : self.flag_value,
            "pos_value" : self.pos_value,
            "type_values" : self.type_values
        }
        for value in dict.values():
            #validate keys
            differs = set(value.keys()) - set(self.structure.keys())
            if differs:
                print(f"args config incorrect: {differs}")
                return False
            else:
                return True #Esto está inacabado
            
    def getPosList(self, pipe): #extract keys list from pipe
        pass
    def validatePipeStructure(self):
        pass


class articFolderManagement(): #Idealmente, debería ser una clase padre FolderManagement y esta ser su hija
    def __init__(self, fastq_pass = "fastq_pass/", fast5_pass = "fast5_pass/", fastq_filter = "fastq_filter/", data_root = "data/", seq_summary = "sequencing_summary*", path = "./"):
        #pendiente la validación del campo. Pendiente gestión de la outfolder!
        def folderFixer(folder):
            if folder[-1] != "/":
                return folder + "/"
            else:
                return folder
        self.fastq_pass = folderFixer(fastq_pass)
        self.fast5_pass = folderFixer(fast5_pass)
        self.fastq_filter = folderFixer(fastq_filter)
        self.data_root = folderFixer(data_root)
        self.path = folderFixer(path)
        self.seq_summary = seq_summary 
    
    def buildPaths(self):
        self.data_root = self.path + self.data_root
        self.fastq_pass = self.data_root + self.fastq_pass
        self.fast5_pass = self.data_root + self.fast5_pass
        self.fastq_filter = self.data_root + self.fastq_filter
        self.seq_summary = self.data_root + self.seq_summary
    
    def getSeqSum(self):
        self.seq_summary_file = glob.glob(self.seq_summary)[0]

    def getListFromFiles(self, folder):
        names_list =  [os.path.splitext(x)[0] for x in os.listdir(folder)]
        return names_list
    def getListFromFolders(self, folder):
        names_list = [x for x in os.listdir(folder)]
        return names_list


class barcoderTool():
    def __init__(self, barcode_header = "barcode", sample_header = "sample"):
        self.barcodeHeader = barcode_header
        self.sampleHeader = sample_header

    def importData(self, file): #De momento para excel. Ampliar a CSV, JSON, TXT...
        try:
            self.df = pd.read_excel(file, engine= "openpyxl", usecols=[self.barcodeHeader, self.sampleHeader], dtype= {self.barcodeHeader: str, self.sampleHeader: str}).dropna(axis=0)    
        except Exception as e:
            print("Cannot open excel file")
            print(e)
            sys.exit(0)

    def fillZero(self, numberZeros = 1, value = "0"): #Ojo, esto no sirve si se le ha metido el prefijo. Añadir subfunción guess: localiza el string más largo y lo rellena en base a
        newBarcodes = []
        len_str = self.df[self.barcodeHeader].astype(int).astype(str).str.len() #Convertimos a int para elimnar los 0 que ya existan y devolvemos a str para el len
        for barcode, length in zip(self.df[self.barcodeHeader], len_str):
            index = numberZeros - length + 1
            if index > 0:
                newBarcode = value * index + str(barcode)
            else:
                newBarcode = barcode
            newBarcodes.append(newBarcode)
        self.df[self.barcodeHeader] = newBarcodes

    def deleteZero(self):
        try:
            self.df[self.barcodeHeader] = self.df[self.barcodeHeader].astype(int)
        except AttributeError:
            print("Exception: Barcodes cannot be coerced to integer")

    def setPreffix(self, prefix, sep=""):
        self.df[self.barcodeHeader] = str(prefix) + str(sep) + self.df[self.barcodeHeader]

    def zipperDataFrame(self):
        zipper = zip(self.df[self.barcodeHeader], self.df[self.sampleHeader])
        return zipper
        
    def listElements(self, element):
        if element in [self.barcodeHeader, self.sampleHeader]:
            return self.df[element].tolist()
        else:
            print("Element not in dataframe")
    def exportDict(self):
        pass

    def printRelation(self):
        pass

class fileExtensions():
    pass


    