#!/usr/bin/env python3
import sys
sys.path.append('/home/microb_ngs/env_scripts/py_scripts/tools')

import argparse
import os
import pipelinesTools.pipeConfig as pipe

###Functions:

def run(pipeConfigEngine, fast5_path):
    cmds = []
    pipeConfigEngine.modArgManually(pipes = {"guppy_basecaller"}, arg = "input_path", value = fast5_path)
    pipeConfigEngine.buildArgs()
    cmds += pipeConfigEngine.buildCMD()
    path = pipeConfigEngine.config["guppy_basecaller"]["save_path"]["value"]
    print(path)
    cmds += [f"mv {path}/{sequencing_summary} ./"]
    for cmd in cmds:
        print(f"Execute: {cmd}")
        os.system(cmd)

####Plan: esta pipe debe realizar el barcoding, el demultiplexing y devolver los archivos en el mismo esquema que requiere artic_pipe para no tener que reprogramar nada

##Constants

scriptDir = os.path.dirname(__file__)
sequencing_summary = "sequencing_summary.txt" #A archivo de constantes!

#Arg parser 
parser = argparse.ArgumentParser(description="Run guppyplex for basecalling and demultiplexing")

parser.add_argument("-f", "--folder", help = "Folder with fast5 data", required=True)
parser.add_argument("-c", "--config", help = "YAML file with pipe config", default=f"{scriptDir}/configFiles/barcoderArgs.yml")


if __name__== "__main__":
    try:
        args = parser.parse_args()
    except:
        print("Use -h command for help")
        sys.exit(0)
    ####cargamos la configuración
    pipeConfigEngine = pipe.pipeConfig(file = args.config)
    ##RUn
    run(pipeConfigEngine, args.folder)