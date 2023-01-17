
import os


# Funciones de configuración -> Convertir en clase también?
###Ir pensando en como capturar la información para volcarlo a la base de datos

def confGuppy(pipeConfigEngine, articFolderEngine, run_name, pipe = "artic guppyplex", ):
    cmds =[]
    #El articfolderengine: añadir método para crear todos los directorios
    if not os.path.exists(articFolderEngine.fastq_filter):
        os.mkdir(articFolderEngine.fastq_filter)
    barcodes_list = articFolderEngine.getListFromFolders(articFolderEngine.fastq_pass)
    #Configuracion del argumento prefix
    pipeConfigEngine.modArgManually(pipes={pipe}, arg = "prefix", value = run_name)
    #Creación de la secuencia de comandos
    for barcode in barcodes_list:
        pipeConfigEngine.modArgManually(pipes={pipe}, arg = "directory", value = f"{articFolderEngine.fastq_pass}{barcode}")
        pipeConfigEngine.buildArgs(pipe = {pipe})
        cmds.append(pipeConfigEngine.buildCMD()[0])
        cmds.append(f"mv {run_name}_{barcode}.fastq {articFolderEngine.fastq_filter}")
    return cmds
        

def confMinion(pipeConfigEngine, articFolderEngine, barcoderEngine, run_name, output_folder, pipe = "artic minion"):
    cmds = []

    #creamos la carpeta de salida
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    
    #definimos los argumentos globales de la ejecución:
    pipeConfigEngine.modArgManually(pipes={pipe}, arg="sequencing-summary", value = articFolderEngine.seq_summary)
    pipeConfigEngine.modArgManually(pipes={pipe}, arg="fast5-directory", value=articFolderEngine.fast5_pass)

    #lista de comandos
    for barcode, sample in barcoderEngine.zipperDataFrame():
        #La función debería chequear previamente los archivos fastq y fast5 para no ejecutar nada que no exista
        pipeConfigEngine.modArgManually(pipes={pipe}, arg="read-file", value=f"{articFolderEngine.fastq_filter}{run_name}_{barcode}.fastq")
        pipeConfigEngine.modArgManually(pipes={pipe}, arg = "sample", value = str(sample)) #Hasta tener desarrollado el modArgFromDict
        pipeConfigEngine.buildArgs(pipe={pipe})
        cmds.append(pipeConfigEngine.buildCMD()[0])
        cmds.append(f"mv {sample}* {output_folder}")
    cmds.append(f"cat {output_folder}*.consensus.fasta > {output_folder}{run_name}.fa") #Este outputfolder puede dar error!!! ¿El fileManager no lo arregla?
    return cmds

#Funciones de gestión de archivos -> Estas deberían ir a la clase de folderManagement

def fileManagerType(folder, file_exceptions = []):
    file_dict ={}
    cmds = []
    for file in os.listdir(folder):
        if os.path.isfile(f"{folder}{file}"):
            file_ext = os.path.splitext(file)[1]
            file_dir = file_ext.lstrip(".")
            file_dict[file_dir] = file_ext 
    cmds += [f"mkdir {folder}{x}" for x in file_dict.keys() if not os.path.isdir(f"{x}")]
    cmds += [f"mv *{folder}{file_ext} {folder}{file_dir}" for file_dir, file_ext in file_dict.items() if file_ext not in file_exceptions]
    return cmds


def fileManagerSample(folder, barcoderEngine, sampleHeader):
    cmds = []
    samples_list = barcoderEngine.listElements(sampleHeader)
    samples_files = {sample.split(".")[0] for sample in os.listdir(folder)}
    validate_samples = {sample for sample in samples_files if sample in samples_list}
    cmds += [f"mkdir {folder}{sample}" for sample in validate_samples]
    cmds += [f"mv {folder}{sample}* {folder}{sample}" for sample in validate_samples]
    return cmds


def fileManager(folder, file_exceptions, barcoderEngine, sampleHeader, storeBySample):
    if not storeBySample:
        cmds = fileManagerType(folder, file_exceptions)
    else:
        cmds = fileManagerSample(folder, barcoderEngine, sampleHeader)
    return cmds

