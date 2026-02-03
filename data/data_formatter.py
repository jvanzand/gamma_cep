import pandas as pd
import numpy as np
from astropy.time import Time

## Filter warnings about dubious year conversions ##
import warnings
from erfa import ErfaWarning
warnings.filterwarnings(
    "ignore",
    category=ErfaWarning,
    message='.*dubious year.*'
)
####################################################


def format_rvs():
    """
    Collect and format available
    RVs for the Gamma Cep system
    
    Saves 2 files: formatted RVs for
                   Octofitter and for 
                   Orvara
    """
    
    # Load and format literature RVs
    lit_rvs = pd.read_csv("lit_files/222404_lit_rvs.dat", delim_whitespace=True, skiprows=9)
    ##############################
    
    # Special treatment for Griffin+02 RVs. Need to manually assign rv_err based on instrument
    ###########################################################################################
    g_lit_rvs = pd.read_csv("lit_files/222404_griffin_lit_rvs.dat", delim_whitespace=True, skiprows=3)
    g_err_dict = {'Lick':0.9, 'Fick':0.5, 'Cambridge':0.8, 'DAO':0.3, 'HP':0.2, 'McDonald':0.03}
    g_lit_rvs['RV_err'] = g_lit_rvs['Instrument'].map(g_err_dict) # Determine rv error based on instrument
    
    g_lit_rvs['rv'] = g_lit_rvs['RV[km/s]']*1000
    g_lit_rvs['rv_err'] = g_lit_rvs['RV_err']*1000
    g_lit_rvs['jd'] = g_lit_rvs['Epoch[MJD]'] + 2400000.5
    g_lit_rvs['tel_ind'] = 0 # Hard coded at 0
    g_lit_rvs = g_lit_rvs.query("Instrument!='McDonald'") # Omit 11 McDonald RVs
    g_lit_rvs = g_lit_rvs[['jd', 'rv', 'rv_err', 'tel_ind']] # Take only the updated rows
    
    new_cols = ['time', 'mnvel', 'errvel', 'tel_ind']
    lit_rvs.columns = new_cols
    g_lit_rvs.columns = new_cols
    ############################################################################################

    
    # Load RVs from Jump
    jump_rvs = pd.read_csv('/data/radvel/input_dir/222404/data/all_data/all_data.csv')
    
    # Load new RVs from Guillermo Torres
    tres_rvs = pd.read_csv('lit_files/222404_TRES_rvs.dat', delim_whitespace=True)
    tres_rvs['time'] = tres_rvs['BJD-2400000']+2400000
    tres_rvs['mnvel'] = tres_rvs['RV']*1000 # Convert km/s --> m/s
    tres_rvs['errvel'] = tres_rvs['err']*1000
    tres_rvs['tel'] = 'tres'
    
    # Load full McDonald III data set
    mcd3_rvs = pd.read_csv('lit_files/222404_McD3_rvs.dat', delim_whitespace=True)
    #import pdb; pdb.set_trace()
    mcd3_rvs['time'] = mcd3_rvs['BJD[d]']
    mcd3_rvs['mnvel'] = mcd3_rvs['dRV[m/s]']
    mcd3_rvs['errvel'] = mcd3_rvs['err[m/s]']
    mcd3_rvs['tel'] = 'mcdonald3'
    ####################################
    
    ## Combine lit_rvs and new_rvs to format columns ##
    lit_rvs = pd.concat([lit_rvs, g_lit_rvs]) # Concatenate Griffin RVs onto lit RVs
    new_rvs = pd.concat([jump_rvs, tres_rvs, mcd3_rvs])[['time', 'mnvel', 'errvel', 'tel']]
    
    #import pdb; pdb.set_trace()
    
    
    ## Dicts to give tel names to the Lit RVs and indices to the Jump RVs ##
    ## Order is based on earliest RV in each set. Doesn't matter as long as it's consistent
    ind2tel = {0:'griffin' , 1:'torres', 2:'cfht', 3:'mcdonald1', 4:'mcdonald2', 
               5:'mcdonald3', 6:'tres', 7:'j', 8:'apf'}
    
    lit_rvs['tel'] = lit_rvs['tel_ind'].map(ind2tel)
    
    tel2ind = {tel:f"{ind}" for ind, tel in ind2tel.items()} # Invert tel_dict above to go back to inds
    new_rvs['tel_ind'] = new_rvs['tel'].map(tel2ind)
    
    
    ## Decide HERE which RVs to include ##
    #import pdb; pdb.set_trace()
    use_tels = ['griffin' , 'torres', 'cfht', 'mcdonald1', 'mcdonald2', 'mcdonald3', 'tres', 'j', 'apf']
    all_rvs = pd.concat([lit_rvs, new_rvs]) # Combine all RVs
    all_rvs = all_rvs.query("tel==@use_tels")
    
    ## Print out useful info about RVs
    print_rv_info(all_rvs)
    #import pdb; pdb.set_trace()


    ## Save RVs in Octofitter format
    octofitter_cols = ["time", "mnvel", "errvel", "tel"]
    all_rvs[octofitter_cols].to_csv('octofitter_all_rvs.csv', index=False) # Save RVs for use in Octofitter
    #import pdb; pdb.set_trace()
    
    ## Save RVs in Orvara format
    orvara_cols = ["time", "mnvel", "errvel", "tel_ind"]
    np.savetxt('orvara_all_rvs.txt', all_rvs[orvara_cols].values, fmt='%s') # Write to text file for Orvara
   
    
    ## Save latex tables for paper
    all_rvs['time_trunc'] = all_rvs['time'] - 2400000.0
    all_rvs['latex_telname'] = all_rvs['tel'].map({'mcdonald3':'McDonald III', 'tres':'TRES', 'j':'HIRES', 'apf':'APF'})
    
                           
             
    use_sigfig_rule = False
    
    if use_sigfig_rule:
        ## If using sigfig rule:  
        latex_cols = ["time_trunc", "rounded_mnvel", "rounded_errvel", "latex_telname"]            
        all_rvs['rounded_errvel'] = all_rvs['errvel'].apply(round_to_1sigfig)
        all_rvs['rounded_mnvel'] = all_rvs.apply(lambda row: round_to_err_precision(row.mnvel, row.errvel), axis=1)
    
    
        format_dict = {
            "time_trunc": "{:.4f}".format,
            "rounded_mnvel": int_if_integer,
            "rounded_errvel": int_if_integer,
        }
        
    else:
        latex_cols = ["time_trunc", "mnvel", "errvel", "latex_telname"]
        format_dict = {
            "time_trunc": "{:.4f}".format,
            "mnvel": "{:.2f}".format,
            "errvel": "{:.2f}".format,
        }
    
    
    all_rvs_latex = all_rvs.query("tel in ['mcdonald3', 'tres', 'j', 'apf']")\
                           .sort_values(by=['tel', 'time'])[latex_cols]
    

    #import pdb; pdb.set_trace()
    all_rvs_latex[latex_cols].to_latex('latex_tables/latex_all_rvs.tex', 
                                  index=False, formatters=format_dict)
    
    return
    
def round_to_1sigfig(err):
    """
    Helper function for format_rvs() above
    Round an RV error to 1 sig fig
    Should take, eg, 0.34-->0.3, 4950-->5000
    """
    if err==0 or np.isnan(err):
        return val
    
    return round(err, -int(np.floor(np.log10(err))))

def round_to_err_precision(val, err):
    """
    Helper function for format_rvs() above
    Round an RV value to the same precision
    as its error
    """
    if err==0 or np.isnan(err):
        return val
    
    power = -int(np.floor(np.log10(err)))
    return round(val, power)
    
def int_if_integer(x):
    """
    Another helper function to convert
    integers to int and leave floats. Eg
    520.0 --> '520' and 100.01 --> '100.01'
    """
    if pd.isna(x):
        return ""
    if float(x).is_integer():
        return str(int(x))
    return str(x) 
    
    
def format_relAst():
    """
    Reformat the RelAst data Brendan
    sent me
    """

    relAst_Bowler = pd.read_csv('lit_files/222404_Bowler_relAST.txt', delim_whitespace=True) # Compiled by Brendan
    relAst_Mugrauer = pd.read_csv('lit_files/222404_Mugrauer_relAST.txt', delim_whitespace=True) # Mugrauer+23
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

def print_rv_info(all_rv_df):
    """
    Print out useful info about the RV data
    
    - How many TOTAL RVs, and between what dates
    - How many PRECISION RVs, and between what dates
    - How many NEW RVs, and between what dates
    - How much time the PRV baseline has been extended
    - How many RVs for each telescope
    
    """

    all_tels = ['griffin' , 'torres', 'cfht', 'mcdonald1', 'mcdonald2', 'mcdonald3', 'tres', 'j', 'apf']
    prv_tels = ['cfht', 'mcdonald1', 'mcdonald2', 'mcdonald3', 'j', 'apf']
    new_rv_tels = ['mcdonald3', 'tres', 'j', 'apf']
    tel_lists = [all_tels, prv_tels, new_rv_tels]
    
    McD3_time_cutoff = 2452839. # McD3 RVs before this are already published

    
    ## Calculate number of total, precision, and new RVs ##
    tel_types = ["total", "precision", "new"]
    for i in range(3):
        tel_list = tel_lists[i]
        tel_type = tel_types[i]
        
        tel_df = all_rv_df.query("tel in @tel_list")
        
        if i==2:
            tel_df = tel_df.query("time>@McD3_time_cutoff")
            
        num_RVs = len(tel_df)
        start_date = Time(tel_df.time.min(), format='jd').iso.split(' ')[0]
        end_date = Time(tel_df.time.max(), format='jd').iso.split(' ')[0]
        
        print(f"{num_RVs} {tel_type} RVs between {start_date} and {end_date}")
        
    ## Calculate how much the observing baseline has been extended ##
    old_rv_tels = [tel for tel in prv_tels if not tel in new_rv_tels]+['mcdonald3']
    old_rvs = all_rv_df.query("tel in @old_rv_tels").query("time<@McD3_time_cutoff") # Take only McD3 before cutoff
    new_rvs = all_rv_df.query("tel in @new_rv_tels")
   
    latest_published_date = Time(old_rvs.time.max(), format='jd').iso.split(' ')[0]
    latest_new_date = Time(new_rvs.time.max(), format='jd').iso.split(' ')[0]
    baseline_extension = np.round((new_rvs.time.max() - old_rvs.time.max())/365.25, 2)
   
    print(f'Extended PRV baseline from {latest_published_date} to {latest_new_date} ({baseline_extension} years)')
    

    
    ## Calculate Num_RVs, baselines, and median errors for each telescope ##
    print("\n"*2)
    #import pdb; pdb.set_trace()
    tels_in_all_rv_df = list(set(all_rv_df.tel))
    tel_order = {tel:i for i, tel in enumerate(all_tels)}
    sorted_tels = sorted(tels_in_all_rv_df, key=lambda x: tel_order[x])
    for telname in sorted_tels:
        sub_timeseries = all_rv_df.query(f"tel=='{telname}'")
        num_RVs = len(sub_timeseries)
        if num_RVs==0:
            continue

        if telname!='torres':
            start_date = Time(sub_timeseries.time.min(), format='jd').iso.split(' ')[0]
            end_date = Time(sub_timeseries.time.max(), format='jd').iso.split(' ')[0]
            median_err = sub_timeseries.errvel.median()
        
            print(f"    {telname}: {num_RVs} RVs between {start_date} and {end_date} with median error of {median_err:.2f} m/s")
            print('')
            
        else:
            #import pdb; pdb.set_trace()
            torres_rvs = sub_timeseries.iloc[:-3]
            mugrauer_rvs = sub_timeseries.iloc[-3:]
            
            ntorres_rvs = len(torres_rvs)
            start_torres = Time(torres_rvs.time.min(), format='jd').iso.split(' ')[0]
            end_torres = Time(torres_rvs.time.max(), format='jd').iso.split(' ')[0]
            median_torres = torres_rvs.errvel.median()
            
            nmug_rvs = len(mugrauer_rvs)
            start_mugrauer = Time(mugrauer_rvs.time.min(), format='jd').iso.split(' ')[0]
            end_mugrauer = Time(mugrauer_rvs.time.max(), format='jd').iso.split(' ')[0]
            median_mugrauer = mugrauer_rvs.errvel.median()
            
            print(f"        torres: {ntorres_rvs} RVs between {start_torres} and {end_torres} with median error of {median_torres:.2f} m/s")
            print('')
            print(f"        mugrauer: {nmug_rvs} RVs between {start_mugrauer} and {end_mugrauer} with median error of {median_mugrauer:.2f} m/s")
            print('')
           
    #import pdb; pdb.set_trace() 
    return

if __name__=="__main__":
    format_rvs()
    format_relAst()




















