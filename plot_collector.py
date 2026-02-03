## Module to collect and rename various Gamma Cep plots for the paper
import os
import shutil
from pathlib import Path


## Local command to copy the folder of collected plots onto my machine:
## 


def copy_and_rename():
    """
    Copy figures to target_dir with new filenames.

    Parameters
    ----------
    None; all paths input manually
    """

    ## Collect figures and tables for paper ##
    root = "/data/user/judahvz/postdoc_projects/gamma_cep/"
    paths_short = ["orvara_fit/outputs_good/companion_0_Temp0/RV_OC_gamma_cep_InstAll.pdf",
                   "orvara_fit/outputs_good/companion_0_Temp0/RV_OC_gamma_cep_Inst[4,5,6].pdf",
                   "orvara_fit/outputs_good/companion_0_Temp0/astrometric_orbit_gamma_cep.pdf",
                   "orvara_fit/outputs_good/companion_0_Temp0/ProperMotions_RA_gamma_cep.pdf",
                   "orvara_fit/outputs_good/companion_0_Temp0/ProperMotions_Dec_gamma_cep.pdf",
                   "orvara_fit/outputs_good/companion_0_Temp0/PA_OC_gamma_cep.pdf",
                   "orvara_fit/outputs_good/companion_0_Temp0/relsep_OC_gamma_cep.pdf",
                   "inj_rec/GammaCep_30BIC/GammaCep_30BIC_recoveries.png"
                   ]
    paths_full = [os.path.join(root, short_path) for short_path in paths_short]

    
    new_names = ['all_rvs.pdf',
	         'precision_rvs.pdf',
	         'astrometric_orbit.pdf',
	         'proper_motion_RA.pdf',
	         'proper_motion_Dec.pdf',
	         'PA.pdf',
	         'RelSep.pdf',
	         'inj_rec.png']
	         
    target_dir = os.path.join(root, 'paper_plots_gamma_cep/')
    

    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    for src, new_name in zip(paths_full, new_names):
        src = Path(src)
        dst = target_dir / new_name
        shutil.copy2(src, dst)
        
    return



if __name__=="__main__":
    copy_and_rename()





























