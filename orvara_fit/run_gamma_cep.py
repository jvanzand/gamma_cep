import os
import sys
import subprocess


def run_orvara(config_path, results_path):
    """
    Run Orvara on a single system
    """

    os.makedirs(results_path, exist_ok=True) # Make sure output directory exists

    ## IMPORTANT: Orvara assumes you will run code in the directory containing Orvara.
    ## I don't want to do this, so instead I must change my working directory temporarily
    ## That means I can't use relative paths for my .ini file and outputs directory
    os.chdir("/Users/judahvz/research/code/GitHub/")
    
    subprocess.run(["fit_orbit", config_path, "--output-dir", results_path])
    # subprocess.run(["plot_orbit", config_path, "--output-dir", results_path])

    return













if __name__=="__main__":
    gamma_cep_root = "/Users/judahvz/research/code/GitHub/gamma_cep/orvara_fit/"
    ini_path = gamma_cep_root+"config_gamma_cep.ini"
    outputs_path = gamma_cep_root+"outputs/"
    run_orvara(ini_path, outputs_path)











