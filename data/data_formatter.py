import pandas as pd
import numpy as np
from astropy.time import Time



def format_rvs():
    """
    Collect and format available
    RVs for the Gamma Cep system
    
    Saves 2 files: formatted RVs for
                   Octofitter and for 
                   Orvara
    """

    # Load RVs from Jump
    jump_rvs = pd.read_csv('222404_jump_rvs.csv')
    
    # Load and format literature RVs
    lit_rvs = pd.read_csv("222404_lit_rvs.dat", delim_whitespace=True, skiprows=9)
    
    new_cols = ['time', 'mnvel', 'errvel', 'tel_ind']
    lit_rvs.columns = new_cols
    
    
    ## Dicts to give tel names to the Lit RVs and indices to the Jump RVs
    ind2tel = {0:'mcdonald1', 1:'torres', 2:'cfht', 3:'mcdonald2', 4:'mcdonald3', 5:'j', 6:'apf'}
    lit_rvs['tel'] = lit_rvs['tel_ind'].map(ind2tel)
    
    tel2ind = {tel:f"{ind}" for ind, tel in ind2tel.items()} # Invert tel_dict above to go back to inds
    jump_rvs['tel_ind'] = jump_rvs['tel'].map(tel2ind)
    
    all_rvs = pd.concat([jump_rvs, lit_rvs]) # Combine all RVs
    
    
    ## Save RVs in Octofitter format
    octofitter_cols = ["time", "mnvel", "errvel", "tel"]
    all_rvs[octofitter_cols].to_csv('octofitter_all_rvs.csv', index=False) # Save RVs for use in Octofitter
    
    ## Save RVs in Orvara format
    orvara_cols = ["time", "mnvel", "errvel", "tel_ind"]
    np.savetxt('orvara_all_rvs.txt', all_rvs[orvara_cols].values, fmt='%s') # Write to text file for Orvara
    
    ## Save latex tables for paper
    all_rvs['time_trunc'] = all_rvs['time'] - 2400000.0
    all_rvs['latex_telname'] = all_rvs['tel'].map({'apf':'APF', 'j':'HIRES', 'mcdonald3':'McDonald III'})
    latex_cols = ["time_trunc", "mnvel", "errvel", "latex_telname"]
    format_dict = {
        "time_trunc": "{:.4f}".format,
        "mnvel": "{:.2f}".format,
        "errvel": "{:.2f}".format,
    }
    
    all_rvs_latex = all_rvs.query("tel in ['j', 'apf', 'mcdonald3']")\
                           .sort_values(by=['tel', 'time'])[latex_cols]
    all_rvs_latex[latex_cols].to_latex('latex_tables/latex_all_rvs.tex', 
                                  index=False, formatters=format_dict)
    
    
    return
    
def format_relAst():
    """
    Reformat the RelAst data Brendan
    sent me
    """

    relAst_Bowler = pd.read_csv('222404_Bowler_relAST.txt', delim_whitespace=True) # Compiled by Brendan
    relAst_Mugrauer = pd.read_csv('222404_Mugrauer_relAST.txt', delim_whitespace=True) # Mugrauer+23
    relAst = pd.concat([relAst_Bowler, relAst_Mugrauer])
    
    relAst['jd'] = Time(relAst.Date, format='decimalyear').jd
    
    relAst['sep_mas'] = relAst['Sep']*1000
    relAst['err_sep_mas'] = relAst['Err_Sep']*1000
    
    relAst['PA_rad'] = relAst['PA']*np.pi/180
    relAst['err_PA_rad'] = relAst['Err_PA']*np.pi/180
    
    octofitter_cols = ['jd', 'sep_mas', 'err_sep_mas', 'PA_rad', 'err_PA_rad', 'Inst']
    relAst[octofitter_cols].to_csv('octofitter_all_relAst.csv', index=False) # Write to csv for Octofitter
    
    #############################################################################################
    ## Orvara formatting requires sep in arcsec and PA in deg, ALSO it doesn't accept instrument indices,
    ## and it DOES require the companion index to be supplied directly in the data
    
    orvara_cols = ['jd', 'Sep', 'Err_Sep', 'PA', 'Err_PA', 'companion_index']
    relAst['companion_index'] = '0' # All relAst corresponds to companion B, so make them all 0
    
    np.savetxt('orvara_all_relAst.txt', relAst[orvara_cols].values, fmt='%s') # Write to text file for Orvara
    
    return




if __name__=="__main__":
    format_rvs()
    format_relAst()




















