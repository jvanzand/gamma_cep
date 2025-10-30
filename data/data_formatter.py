import pandas as pd
import numpy as np
from astropy.time import Time



def format_rvs():
    """
    Collect and format available
    RVs for the Gamma Cep system
    """

    # Load RVs from Jump
    jump_rvs = pd.read_csv('222404_jump_rvs.csv')
    
    # Load and format literature RVs
    lit_rvs = pd.read_csv("222404_lit_rvs.dat", delim_whitespace=True, skiprows=9)
    
    new_cols = ['time', 'mnvel', 'errvel', 'tel_ind']
    lit_rvs.columns = new_cols
    
    tel_dict = {0:'mcdonald1', 1:'torres', 2:'cfht', 3:'mcdonald2', 4:'mcdonald3'}
    lit_rvs['tel'] = lit_rvs['tel_ind'].map(tel_dict)
    lit_rvs = lit_rvs.drop(columns='tel_ind')
    #########


    all_rvs = jump_rvs.append(lit_rvs) # Combine all RVs
    all_rvs.to_csv('all_rvs.csv', index=False)
    
    return
    
def format_relAst():
    """
    Reformat the RelAst data Brendan
    sent me
    """
    
    relAst_Bowler = pd.read_csv('222404_Bowler_relAst.txt', delim_whitespace=True) # Compiled by Brendan
    relAst_Mugrauer = pd.read_csv('222404_Mugrauer_relAst.txt', delim_whitespace=True) # Mugrauer+23
    relAst = pd.concat([relAst_Bowler, relAst_Mugrauer])
    
    relAst['jd'] = Time(relAst.Date, format='decimalyear').jd
    
    relAst['sep_mas'] = relAst['Sep']*1000
    relAst['err_sep_mas'] = relAst['Err_Sep']*1000
    
    relAst['PA_rad'] = relAst['PA']*np.pi/180
    relAst['err_PA_rad'] = relAst['Err_PA']*np.pi/180
    
    keep_cols = ['jd', 'sep_mas', 'err_sep_mas', 'PA_rad', 'err_PA_rad', 'Inst']
    relAst[keep_cols].to_csv('all_relAst.csv', index=False)
    
    return




if __name__=="__main__":
    format_rvs()
    format_relAst()




















