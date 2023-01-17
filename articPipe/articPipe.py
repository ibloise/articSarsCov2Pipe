#!/usr/bin/env python3
import sys
sys.path.append('/home/microb_ngs/env_scripts/py_scripts/tools')

import argparse
import os
import pipelinesTools.pipeConfig as pipe
from functions import *


#function:

def checkEnv(executeEnv):
    if os.environ["CONDA_DEFAULT_ENV"] != executeEnv:
        print(f"Incorrect environment. Please, execute conda activate {executeEnv}")
        sys.exit(0)

def run(pipeConfigEngine, articFolderEngine, barcoderEngine, runName, outFolder, fileExceptions, sampleHeader, skipGuppy, storeBySample):
    cmds = []
    if not skipGuppy:
        cmds += confGuppy(pipeConfigEngine, articFolderEngine, run_name=runName)
    cmds += confMinion(pipeConfigEngine, articFolderEngine, barcoderEngine, runName, outFolder)
    cmds += fileManager(outFolder, fileExceptions, barcoderEngine, sampleHeader, storeBySample)
    for cmd in cmds:
        print(f"Execute: {cmd}")
        os.system(cmd)

#Constants
scriptDir = os.path.dirname(__file__)
executeEnv = "artic-ncov2019" #a archivo de constantes
file_exceptions = [".fa", ".log"] #A archivo de constantes

##Run the artic pipe 

##ArgParser

parser = argparse.ArgumentParser(description="Run artic pipeline for SARS-CoV-2 minion data.")

parser.add_argument("-x", "--excel", help = "Excel file with the relation between barcodes and samples", required=True)
parser.add_argument("-r", "--run_name", help = "Name of the run", required=True)
parser.add_argument("-b", "--barcode", help = "Header name of barcodes column", default= "barcode")
parser.add_argument("-s", "--sample", help = "Header name of samples column", default = "sample")
parser.add_argument("-p", "--prefix", help = "Barcode prefix in the files", default= "barcode")
parser.add_argument("--prefix_sep", help="Separator betwenn barcode prefix and value", default="")
parser.add_argument("-n", "--no_fill", help = "Unnable fill barcodes with 0", action="store_true")
parser.add_argument("-c", "--config", help = "Path to config file in yaml format", default= f"{scriptDir}/configFiles/articArgs.yml")
parser.add_argument("--output_folder", help = "Name of output folder", default="output/")
parser.add_argument("--data_folder", help = "Path to folder with the data", default= "data/")
parser.add_argument ("--skip_guppy", help = "Skip artic guppyplex", action="store_true")
parser.add_argument("--store_by_sample", help = "Change behaviour of the file management functions. Store the output files by sample instead of by type", type=bool)


if __name__== "__main__":
    #Check environment
    checkEnv(executeEnv)
    #Check args

    try:
        args = parser.parse_args()
    except:
        print("Use -h command for help")
        sys.exit(0)

    #Leemos los barcodes
    barcoderData = pipe.barcoderTool(barcode_header= args.barcode, sample_header= args.sample)
    barcoderData.importData(file = args.excel)
    
    if not args.no_fill:
        barcoderData.fillZero()

    if args.prefix:
        barcoderData.setPreffix(prefix=args.prefix, sep=args.prefix_sep)

    #Cargamos la configuración de la pipeline

    pipeConfigEngine = pipe.pipeConfig(file=args.config)

    #Cargamos el gestor de carpetas

    articFolderEngine = pipe.articFolderManagement(data_root=args.data_folder)

    #Construcción de la rutas

    articFolderEngine.buildPaths()

    ##Ejecutamos

    run(pipeConfigEngine, articFolderEngine, barcoderData, runName= args.run_name, outFolder= args.output_folder, fileExceptions= file_exceptions, sampleHeader=args.sample, skipGuppy=args.skip_guppy, storeBySample=args.store_by_sample)