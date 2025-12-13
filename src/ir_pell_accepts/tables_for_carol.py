import pandas as pd
from pathlib import Path

from ir_pell_accepts.headcount_calcs import filter_enrollment_table
from ir_pell_accepts.helper import calc_academic_year_from_term


def generate_ipeds_table_for_carol(dfr: pd.DataFrame, acad_year: str, outpath: str | Path) -> None:
    """
    # TEST Generate a table of student IDs for students cohorted into any term of the provided academic year. 
    
        This is for Carol to add two flags:
        
            1. Pell recipient.
            
            2. Stafford or Direct Subsidized Loan recipient.

        This is being used for the ATI-Kessler report.

        The file name is created inside the function.

        Only necessary columns are output.
    
    Parameters
    ----------
    > dfr : pandas DataFrame
        
        Undergraduate Retention and Graduation table.

    > acad_year : string

        Academic year, e.g., '2025-2026'.

    > outpath : string or Path object
        
        Folder where the table is to be saved.
        Do not include a file name.
    
    Returns
    -------
    > None
        
        Nothing is returned. 

    Example
    -------
    > term = '202580'

    > outpath = '/c/Users/sruddy1'

        result

            Output filtered table to

                '/c/Users/sruddy1/2025-2026 All-Cohorts Student IDs from Undergraduate Retention and Graduation.xlsx'
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
    outfile = Path(outpath) / Path(filename)
        
    df.to_excel(outfile, index=False)

    return None


def generate_table_for_carol(dfe: pd.DataFrame, term: str, outpath: str | Path) -> None:
    """
    # Generate a table of student IDs for all enrolled students for the given academic period, and output as an excel file.
    
        This is for Carol to add two flags:
        
            1. Pell recipient
            
            2. First generation

        This is being used for the ATI-Kessler report.

        The file name is created inside the function.

        Only necessary columns are output.
    
    Parameters
    ----------
    > dfe : pandas DataFrame
        
        Census Date Enrollment table.
    
    > term : string

        Academic period: e.g., '202580'.

    > outpath : string or Path object
        
        Folder where the table is to be saved.
        Do not include a file name.
    
    Returns
    -------
    > None
        
        Nothing is returned. 

    Example
    -------
    > term = '202580'

    > outpath = '/c/Users/sruddy1'

        result

            Output filtered table to

                '/c/Users/sruddy1/Fall 2025 Enrolled Full-Time Student IDs from Census Data Enrollment.xlsx'
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
    outfile = Path(outpath) / Path(filename)
        
    df.to_excel(outfile, index=False)

    return None


