import pandas as pd
from pathlib import Path

from ir_pell_accepts.headcount_calcs import filter_enrollment_table
from ir_pell_accepts.helper import calc_academic_year_from_term


def generate_table_for_carol(dfe: pd.DataFrame, term: str, outpath: Path) -> None:
    """
    Generate a table of student IDs for all enrolled students for Carol to input Pell recipient and First Gen flag
    
    Params
    ------
    dfe : pd.DataFrame
        This is the census data enrollment table
    term :
        generally the current fall term
    outpath : Path object
        folder where the table is to be saved
    """
    dfe = filter_enrollment_table(dfe=dfe, term=term)
    aid_year = calc_academic_year_from_term(term, two_digit=False)

    df = pd.DataFrame({
        'ID'                : dfe['ID'],
        'Person Uid'        : dfe['Person Uid'],
        'Academic Period'   : term,
        'Aid Year'          : aid_year
    })

    filename = " ".join(["Fall", term[:4], "Enrolled Full-Time Student IDs from Census Data Enrollment.xlsx"])
    outfile = outpath / Path(filename)
        
    df.to_excel(outfile, index=False)

    return None


def generate_ipeds_table_for_carol(dfr: pd.DataFrame, acad_year: str, outpath: Path) -> None:
    """
    Generate a table of student IDs for students cohorted into any term of the provided academic year for Carol to input Pell & Stafford recipient flags
    
    Params
    ------
    dfr : pd.DataFrame
        Undergraduate retention file
    acad_year : str
        ex: 2025-2026
    outpath : Path object
        folder where the table is to be saved
    """
    fiscal_year = acad_year[-4:]

    dfr = dfr[dfr['Cohort Fiscal Year'] == fiscal_year]

    df = pd.DataFrame({
        'ID'            : dfr['ID'],
        'Person Uid'    : dfr['Person Uid'],
        'Cohort'        : dfr['Cohort'],
        'Cohort Term'   : dfr['Cohort Academic Period']
    })

    filename = " ".join([acad_year, "All-Cohorts Student IDs from Undergraduate Retention and Graduation.xlsx"])
    outfile = outpath / Path(filename)
        
    df.to_excel(outfile, index=False)

    return None

