import os
import sys
import subprocess
import numpy as np
from astropy.io import fits

orvara_path = "/data/users/judahvz/planet_bd/orvara"
sys.path.insert(0, orvara_path)
from orvara.format_fits import burnin_chain


def run_orvara(config_path, results_path):
    """
    Run Orvara on a single system
    
    Provide the parent directory to Orvara so that this 
    code can be run either locally or on Cadence
    """


    ## IMPORTANT: Orvara assumes you will run code in the directory containing Orvara.
    ## I don't want to do this, so instead I must change my working directory temporarily
    os.chdir(orvara_parent_path)
    
    os.makedirs(results_path, exist_ok=True) # Make sure output directory exists
    #subprocess.run(["fit_orbit", config_path, "--output-dir", results_path])
    subprocess.run(["plot_orbit", config_path, "--output-dir", results_path])
    
    os.chdir(gamma_cep_path) # Now change back

    return



def prep_config():
    """
    To make this code executable both on my machine
    and on Cadence, I need to update the .ini file
    to reflect the new paths. These paths should be
    relative to the Orvara parent path, which will be
    the CWD when Orvara is run.
    """
    lines = []
    with open("config_gamma_cep.ini", "r") as conf_file:
        for line in conf_file:
        
            #if line.startswith("HGCAFile"):
             #   hgca_path = os.path.join(orvara_parent_path, "orvara/HGCA_vEDR3.fits")
              #  line = "HGCAFile = "+hgca_path+"\n"
        
            if line.startswith("RVFile"):
                rv_path = os.path.join(orvara_to_gamma_cep, "../data/orvara_all_rvs.txt")
                line = "RVFile = "+rv_path+"\n"
                
            elif line.startswith("AstrometryFile"):
                relAst_path = os.path.join(orvara_to_gamma_cep, "../data/orvara_all_relAst.txt")
                line = "AstrometryFile = "+relAst_path+"\n"
                
            elif line.startswith("GaiaDataDir"):
                gaia_data_dir_path = os.path.join(orvara_parent_path, "orvara/tests/data/gaia/")
                line = "GaiaDataDir = "+gaia_data_dir_path+"\n"
                
            elif line.startswith("Hip1DataDir"):
                hip1_data_dir_path = os.path.join(orvara_parent_path, "orvara/tests/data/hip1/")
                line = "Hip1DataDir = "+hip1_data_dir_path+"\n"

            elif line.startswith("Hip2DataDir"):
                hip2_data_dir_path = os.path.join(orvara_parent_path, "orvara/tests/data/hip2/")
                line = "Hip2DataDir = "+hip2_data_dir_path+"\n"
            
            elif line.startswith("start_file"):
                start_file_path = os.path.join(orvara_to_gamma_cep, "start_gamma_cep.txt")
                line = "start_file = "+start_file_path+"\n"
                
            elif line.startswith("McmcDataFile"):
                mcmc_output_path = os.path.join(orvara_to_gamma_cep, "outputs/gamma_cep_Temp0_chain000.fits")
                line = "McmcDataFile = "+mcmc_output_path+"\n"
                
            lines.append(line)
        conf_file.close()
        
    with open("config_gamma_cep.ini", "w") as conf_file:
        conf_file.writelines(lines)
        
        conf_file.close()

        
    return

def calculate_params_from_chains():
    """
    Load the MCMC chain from the Gamma Cep
    fit and use it to calculate extra values
    """
    
    chain_path = "outputs_good/gamma_cep_Temp0_chain000.fits"
    chain_columns = ['inc0', 'asc0', 
                     'msec1', 'inc1', 'asc1']
    
    chain = fits.open(chain_path)[1].data
    chain = burnin_chain(chain.columns, 80000, reshape=True)
    
    
    m1sini_chain = chain['msec1']*np.sin(chain['inc1']) * 1047.57 # Convert to M_J
    m1sini_med, m1sini_err = np.median(m1sini_chain), m1sini_chain.std()
    
    # Formula for mutual inclination from Eq. 2 of Huang & Ji (2022), which they got from Gellert+1997
    i_mut_chain = np.arccos(    np.cos(chain['inc0'])*np.cos(chain['inc1'])\
                               +np.sin(chain['inc0'])*np.sin(chain['inc1'])*np.cos(chain['asc0']\
                                                                                  -chain['asc1']))*180/np.pi
    i_mut_med, i_mut_err = np.median(i_mut_chain), i_mut_chain.std()
    
    
    print(f"Companion Msini: {m1sini_med} +/- {m1sini_err} M_Jup") 
    print(f"Mutual inclination: {i_mut_med} +\- {i_mut_err} deg")
    
    #import pdb; pdb.set_trace()
    
    return
    





if __name__=="__main__":
    
    gamma_cep_path = os.getcwd() # Preserve CWD of gamma cep Orvara script
    #orvara_parent_path = "/Users/judahvz/research/code/GitHub/" # Local Orvara parent dir
    orvara_parent_path = "/data/user/judahvz/planet_bd/" # Cadence Orvara parent dir
    orvara_to_gamma_cep = os.path.relpath(gamma_cep_path, start=os.path.dirname(orvara_parent_path))
    
    #prep_config()
    
    
    conf_path = os.path.join(orvara_to_gamma_cep, "config_gamma_cep.ini")
    outputs_path = os.path.join(orvara_to_gamma_cep, "outputs/")
    run_orvara(conf_path, outputs_path) # Run Orvara
    
    calculate_params_from_chains()
    #import pdb; pdb.set_trace()
    
    











