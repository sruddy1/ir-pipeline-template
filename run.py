#!/usr/bin/env python
# coding: utf-8

# # Pell Report (Fall 25)
# ## Documentation
#     - https://udayton.app.box.com/folder/353055993479 - Pell Grant Reporting.docx
#     - (my-SR) Email: https://mail.google.com/mail/u/0/#inbox/FMfcgzQcqtlTMGnlLKdkfVNwlMWwMgjq
# 
# 

# In[2]:


## Load Packages

# system
from pathlib import Path
import sys

# external software
import yaml

# python internal
import pandas as pd
from datetime import date
from importlib.metadata import version
from datetime import date

# Project Packages
from ir_pell_accepts.io_utils import infer_and_read_file, output_results
from ir_pell_accepts.paths import CONFIG_PATH
from ir_pell_accepts.headcount_calcs import (grs_cohort_pell, grs_cohort, total_headcount, 
                                            fall_enrollment, grs_cohort_grad, grs_cohort_pell_grad, 
                                            second_year_retention_rate, second_year_retention_rate_pell)
from ir_pell_accepts.clean import remove_leading_zeros
from ir_pell_accepts.helper import calc_percent, construct_cohort, adjust_term
from ir_pell_accepts.tables_for_carol import generate_table_for_carol, generate_ipeds_table_for_carol


# In[3]:


## Jupyter-Notebook Only -- comment-out when creating .py script

# pd.set_option('display.max_rows', 1000)
# pd.set_option('display.max_columns', 1000)
# pd.set_option('display.max_seq_items', 1000)


# In[3]:


## Load Configuration File and store its values

# Check for config file
if not CONFIG_PATH.exists():
    raise FileNotFoundError(
        f"Config file not found at {CONFIG_PATH}. "
        "Create ir-<project>-<name>/configs/config.yaml to execute code"
    )

with CONFIG_PATH.open("r") as f:
    config = yaml.safe_load(f)

# File and folder paths
BOX_ROOT = Path(config["box_repo"]["box_root"]).expanduser()
PELL_PATH = BOX_ROOT / Path(config["box_repo"]["pell_dir"]).expanduser() / Path(config["box_repo"]["pell_file"]).expanduser()
RETENTION_PATH = BOX_ROOT / Path(config["box_repo"]["retention_dir"]).expanduser() / Path(config["box_repo"]["retention_file"]).expanduser()
ENROLLMENT_PATH = BOX_ROOT / Path(config["box_repo"]["enrollment_dir"]).expanduser() / Path(config["box_repo"]["enrollment_file"]).expanduser()
RESULTS_PATH = BOX_ROOT / Path(config["box_repo"]["results_dir"])
RESULTS_FILE = RESULTS_PATH / Path(config["box_repo"]["results_file"])

# Project Parameters
term = config["params"]["term"] 
ipeds_acad_year = config["params"]["ipeds_acad_year"] 
retention_cohort_term = adjust_term(term=term, years=-1)
grad_term_4 = adjust_term(term=term, years=-4)
grad_term_6 = adjust_term(term=term, years=-6)
id_column = config["params"]["id_column"]


# In[3]:


# Test configuation inputs
if not BOX_ROOT.exists():
    raise FileNotFoundError(f"Box repo path does not exist: {BOX_ROOT}")

if not PELL_PATH.exists():
    raise FileNotFoundError(f"Input Pell file does not exist: {PELL_PATH}")

if not RETENTION_PATH.exists():
    raise FileNotFoundError(f"Input Retention file does not exist: {RETENTION_PATH}")

if not ENROLLMENT_PATH.exists():
    raise FileNotFoundError(f"Input Retention file does not exist: {ENROLLMENT_PATH}")

if not RESULTS_FILE.parent.exists():
    raise FileNotFoundError(f"Results path does not exist: {RESULTS_FILE.parent}")

if len(term) != 6:
    raise ValueError(f"Value for term, {term}, is invalid. Needs to be a 6 digit numeric. Ex: '202580'")


# In[4]:


# Read in files (all columns coverted to strings)
df_pell = infer_and_read_file(PELL_PATH)
df_ret  = infer_and_read_file(RETENTION_PATH)
df_enrl = infer_and_read_file(ENROLLMENT_PATH)


# In[5]:


# Standardize ID column
df_pell = remove_leading_zeros(df_pell, column=id_column)
df_ret  = remove_leading_zeros(df_ret, column=id_column)
df_enrl = remove_leading_zeros(df_enrl, column=id_column)


# In[6]:


# Incoming first-time students
##
pell_first = grs_cohort_pell(dfp=df_pell, dfr=df_ret, id_column='ID', term=term, 
                            aid_year_column='AID_YEAR', cohort_column='Cohort Name')
cohort_first = grs_cohort(dfr=df_ret, id_column='ID', term=term, cohort_column='Cohort Name')

pell_first_grad_4 = grs_cohort_pell_grad(dfp=df_pell, dfr=df_ret, id_column='ID', term=grad_term_4, years_to_grad = 4,
                            aid_year_column='AID_YEAR', cohort_column='Cohort Name')
pell_first_grad_6 = grs_cohort_pell_grad(dfp=df_pell, dfr=df_ret, id_column='ID', term=grad_term_6, years_to_grad = 6,
                            aid_year_column='AID_YEAR', cohort_column='Cohort Name')

cohort_first_grad_4 = grs_cohort_grad(dfr=df_ret, id_column='ID', term=grad_term_4, years_to_grad=4, cohort_column='Cohort Name')
cohort_first_grad_6 = grs_cohort_grad(dfr=df_ret, id_column='ID', term=grad_term_6, years_to_grad=6, cohort_column='Cohort Name')

cohort_first_retention = second_year_retention_rate(dfr=df_ret, id_column='ID', term=retention_cohort_term, cohort_column='Cohort Name')
pell_first_retention = second_year_retention_rate_pell(dfp=df_pell, dfr=df_ret, id_column='ID', term=retention_cohort_term, 
                             aid_year_column='AID_YEAR', cohort_column='Cohort Name')
##


# Total fall enrollment
headcount = total_headcount(dfe=df_enrl, term=term, id_column=id_column)


# Separate out incoming transfer students (nottr = not an incoming transfer student)
###
headcount_nottr = fall_enrollment(dfp=df_pell, dfr=df_ret, dfe=df_enrl, id_column=id_column, term=term, pell=False, transfer=False)
pell_nottr = fall_enrollment(dfp=df_pell, dfr=df_ret, dfe=df_enrl, id_column=id_column, term=term, pell=True, transfer=False)
headcount_transfer = fall_enrollment(dfp=df_pell, dfr=df_ret, dfe=df_enrl, id_column=id_column, term=term, pell=False, transfer=True)
transfer_pell = fall_enrollment(dfp=df_pell, dfr=df_ret, dfe=df_enrl, id_column=id_column, term=term, pell=True, transfer=True)
###


# Calculate Percentages to 2 percentage decimal points
##
pell_first_pct = calc_percent(pell_first, cohort_first)
pell_nottr_pct = calc_percent(pell_nottr, headcount_nottr, 2)
pell_transfer_pct = calc_percent(transfer_pell, headcount_transfer, 2)
##

cohort_fg = pd.NA
pell_fg = pd.NA
cohort_nfg = pd.NA
cohort_ufg = pd.NA
def_fg = pd.NA
comp_fg = pd.NA


# In[7]:


## Collect results by cohort

current_term_metrics = {
    'grs_cohort'                : cohort_first,
    'grs_cohort_pell'           : pell_first,
    'fall_enrollment'           : headcount_nottr,
    'fall_enrollment_pelll'     : pell_nottr,
    'fall_transfer_enrollment'  : headcount_transfer,
    'fall_transfer_enroll_pell' : transfer_pell,
    'total_enrollment'          : headcount,
    'firstgen_enroll'           : cohort_fg,
    'firstgen_enroll_pell'      : pell_fg,
    'continuing_gen_enroll'     : cohort_nfg,
    'unknown_firstgen_enroll'   : cohort_ufg,
    'firstgen_definition'       : def_fg,
    'complete_firstgen'         : comp_fg
}

retention_term_metrics ={
    'retention_rate'      : cohort_first_retention,
    'retention_rate_pell' : pell_first_retention
}

grad4_term_metrics = {
    'grs_cohort_grad_4yr'      : cohort_first_grad_4,
    'grs_cohort_pell_grad_4yr' : pell_first_grad_4
}

grad6_term_metrics = {
    'grs_cohort_grad_6yr'      : cohort_first_grad_6,
    'grs_cohort_pell_grad_6yr' : pell_first_grad_6
}



# In[8]:


# Combine Results

df_curr_term = pd.DataFrame({
    'Cohort' : " ".join(["Fall", term[:4]]),
    'Metric' : current_term_metrics.keys(),
    'Value'  : current_term_metrics.values()
})

df_retention_term = pd.DataFrame({
    'Cohort' : " ".join(["Fall", retention_cohort_term[:4]]),
    'Metric' : retention_term_metrics.keys(),
    'Value'  : retention_term_metrics.values()
})

df_grad4_term = pd.DataFrame({
    'Cohort' : " ".join(["Fall", grad_term_4[:4]]),
    'Metric' : grad4_term_metrics.keys(),
    'Value'  : grad4_term_metrics.values()
})

df_grad6_term = pd.DataFrame({
    'Cohort' : " ".join(["Fall", grad_term_6[:4]]),
    'Metric' : grad6_term_metrics.keys(),
    'Value'  : grad6_term_metrics.values()
})

df_results = pd.concat([
    df_curr_term,
    df_retention_term,
    df_grad4_term,
    df_grad6_term
])


# In[10]:


# Output Tables for Carol

generate_table_for_carol(dfe=df_enrl, term=term, outpath=RESULTS_PATH)
generate_ipeds_table_for_carol(dfr=df_ret, acad_year=ipeds_acad_year, outpath=RESULTS_PATH)
generate_ipeds_table_for_carol(dfr=df_ret, acad_year="-".join([str(int(ipeds_acad_year[:4]) - 1), str(int(ipeds_acad_year[-4:]) - 1)]), outpath=RESULTS_PATH)


# In[ ]:


# Output results

output_results(df=df_results, file_path=RESULTS_FILE, append_today=False, append_version=False)


# In[ ]:




