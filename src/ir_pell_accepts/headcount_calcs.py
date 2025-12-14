import pandas as pd
from ir_pell_accepts.helper import calc_academic_year_from_term, construct_cohort, adjust_term, filter_enrollment_table
from ir_pell_accepts.checks import (validate_columns, required_cohort_columns, 
                                    required_enrollment_columns, required_pell_columns)


def fall_enrollment(
    dfp: pd.DataFrame,
    dfr: pd.DataFrame,
    dfe: pd.DataFrame,
    id_column: str,
    term: str,
    pell: bool = False,
    transfer: bool = False
) -> int:
    """
    # Calculate enrollment headcounts for 4 full-time undergraduate student subpopulations in the provided academic period/term.

        1. All students minus incoming transfer students. (includes pell and non-pell)

        2. All pell recipients minus those that are incoming transfer students.
        
        3. All incoming transfer students. (includes pell and non-pell)
        
        4. All pell recipients that are strictly incoming transfer students.

    Parameters
    ----------
    > dfp : pandas DataFrame
        
        Pell table.
    
    > dfr : pandas DataFrame
        
        Undergraduate Retention and Graduation table.
    
    > dfe : pandas DataFrame
        
        Census Date Enrollment table.
    
    > id_column : string
        
        The name of the column being used to identify students. 
        Applies to all dataframes.

    > term : string

        Academic period: e.g., '202580'.

    > pell : boolean (True/False)

    >> default : False

        True: restrict to pell recipients.
        
        False: include both pell and non-pell students.

    > transfer : boolean (True/False)

    >> default : False
    
        True: restrict to incoming transfer students.

        False: remove incoming transfer students.

    <mark>Note:</mark> `pell` and `transfer` combine to create the 4 aforementioned student subpopulations.

    Returns
    -------
    > integer
        
        Headcount for a given student subpopulation. 

    Example
    -------
    > term = '202580'

    > id_column = 'ID'

    > pell = True

    > transfer = False

        return 
        
            1217

            The number of pell recipients that are not incoming transfer students. 
    #
    """
    validate_columns(df=dfp, id_column=id_column, required_cols=required_pell_columns())
    validate_columns(df=dfr, id_column=id_column, required_cols=required_cohort_columns())
    validate_columns(df=dfe, id_column=id_column, required_cols=required_enrollment_columns())

    dfe = filter_enrollment_table(dfe=dfe, term=term)

    aid_year = calc_academic_year_from_term(term) 
    incoming_transfer_cohort = term[0:4] + " " + "Fall, Transfer, Full-Time"
    
    pids = dfp.loc[dfp['AID_YEAR'] == aid_year, id_column].dropna()
    eids = dfe[id_column].dropna()
    rids = dfr.loc[dfr['Cohort Name'] != incoming_transfer_cohort, id_column].dropna()
    rids_t = dfr.loc[dfr['Cohort Name'] == incoming_transfer_cohort, id_column].dropna()
         
    n_pell_intr = len(set(pids) & set(eids) & set(rids_t))
    
    if not pell and not transfer:
        # size = len(set(eids) & set(rids)) # due to some students have too old of a cohort to be found in the cohort/retention file, they are being included in the fall enrollment non-incoming group. Hence "size = " has been updated to be the difference between the total enrollment minus the total incoming transfer
        size = len(set(eids)) - len(set(rids_t))
    elif pell and not transfer:
        # size = len(set(eids) & set(rids)) # due to some students have too old of a cohort to be found in the cohort/retention file, they are being included in the fall enrollment non-incoming group. Hence "size = " has been updated to be the difference between the total enrollment minus the total incoming transfer pell
        size = len(set(pids) & set(eids)) - n_pell_intr
    elif not pell and transfer:
        size = len(set(eids) & set(rids_t))
    else:
        size = n_pell_intr

    # Return overlap size
    return size


def grs_cohort(
    dfr: pd.DataFrame,
    id_column: str,
    term: str,
    cohort_column: str = "Cohort Name"
) -> int:
    """
    # Calculate the First-Time, Full-Time cohort size for the provided academic period/term.

    Parameters
    ----------
    > dfr : pandas DataFrame
        
        Undergraduate Retention and Graduation table.
    
    > id_column : string
        
        The name of the column being used to identify students. 
        Applies to all dataframes.

    > term : string

        Academic period: e.g., '202580'.

    > cohort_column : str
    
    >> default : 'Cohort Name'
        
        Column in the 'Undergraduate Retention and Graduation'
        dataframe that stores the cohort names in the format 
        '2025 Fall, First-Time, Full-Time'
    
    Returns
    -------
    > integer
        
        Size of the implied cohort.

    Example
    -------
    > term = '202580'

    > id_column = 'ID'

    > cohort_column = 'Cohort Name'
    
        return 
        
            1571
    #
    """
    validate_columns(df=dfr, id_column=id_column, required_cols=required_cohort_columns())

    cohort = construct_cohort(term)
    return sum(dfr[cohort_column] == cohort)


def grs_cohort_grad(
    dfr: pd.DataFrame,
    id_column: str,
    term: str,
    years_to_grad: int,
    cohort_column: str = "Cohort Name"
) -> float:
    """
    # N-year FED graduation rate for the provided academic period.

    Parameters
    ----------
    > dfr : pandas DataFrame
        
        Undergraduate Retention and Graduation table.

    > id_column : string
        
        The name of the column being used to identify students. 
        Applies to all dataframes.

    > term : string

        Academic period: e.g., '202580'.

    > years_to_grad : integer

        The number of years to graduation for which to calculate the graduation rate.  

    > cohort_column : str
    
    >> default : 'Cohort Name'
        
        Column in the 'Undergraduate Retention and Graduation'
        dataframe that stores the cohort names in the format 
        '2025 Fall, First-Time, Full-Time'

    Returns
    -------
    > decimal float
        
        Graduation rate rounded to 3 decimal places. 

    Example
    -------
    > term = '202180'

    > id_column = 'ID'

    > cohort_column = 'Cohort Name'

    > years_to_grad = 4

        return 
        
            0.703
        
            The graduation rate of the 2021 FED cohort. 
    #
    """
    validate_columns(df=dfr, id_column=id_column, required_cols=required_cohort_columns())

    cohort = construct_cohort(term)
    cond1 = dfr[cohort_column] == cohort
    cond2 = pd.to_numeric(dfr['Years to Graduation'].dropna(), errors='coerce') <= years_to_grad

    n_grad = sum(cond1 & cond2)
    n_tot = grs_cohort(dfr=dfr, id_column=id_column, term=term, cohort_column=cohort_column)
    
    return round(n_grad / n_tot, 3)


def grs_cohort_pell(
    dfp: pd.DataFrame,
    dfr: pd.DataFrame,
    id_column: str,
    term: str,
    aid_year_column: str = "AID_YEAR",
    cohort_column: str = "Cohort Name"
) -> int:
    """
    # Calculate the number of Pell recipients for the given aid year and the 'Fall, First-Time, Full-Time' cohort.

    Parameters
    ----------
    > dfp : pandas DataFrame
        
        Pell table.
    
    > dfr : pandas DataFrame
        
        Undergraduate Retention and Graduation table.
    
    > id_column : string
        
        The name of the column being used to identify students. 
        Applies to all dataframes.

    > term : string

        Academic period: e.g., '202580'.

    > aid_year_column : str
    
    >> default : 'AID_YEAR'
        
        Column name in the Pell table dataframe for aid year.
    
    > cohort_column : str
    
    >> default : 'Cohort Name'
        
        Column in the 'Undergraduate Retention and Graduation'
        dataframe that stores the cohort names in the format 
        '2025 Fall, First-Time, Full-Time'
    
    Returns
    -------
    > integer
        
        Number of Pell recipients in the given aid year that
        are Fall, First-Time, Full-Time.

    Example
    -------
    > term = '202580'

    > id_column = 'ID'

    > aid_year_column = 'AID_YEAR'

    > cohort_column = 'Cohort Name'
    
        return 
            
            343
    #
    """
    validate_columns(df=dfp, id_column=id_column, required_cols=required_pell_columns())
    validate_columns(df=dfr, id_column=id_column, required_cols=required_cohort_columns())

    aid_year = calc_academic_year_from_term(term)
    cohort = construct_cohort(term)
    # Filter IDs by aid year and cohort
    pids = dfp.loc[dfp[aid_year_column] == aid_year, id_column].dropna()
    rids = dfr.loc[dfr[cohort_column] == cohort, id_column].dropna()

    # Return overlap size
    return len(set(pids) & set(rids))


def grs_cohort_pell_grad(
    dfp: pd.DataFrame,
    dfr: pd.DataFrame,
    id_column: str,
    term: str,
    years_to_grad: int,
    aid_year_column: str = "AID_YEAR",
    cohort_column: str = "Cohort Name"
) -> int:
    """
    # N-year Pell recipient graduation rate for the FED cohort and the provided academic period.

    Parameters
    ----------
    > dfp : pandas DataFrame
        
        Pell table.
    
    > dfr : pandas DataFrame
        
        Undergraduate Retention and Graduation table.

    > id_column : string
        
        The name of the column being used to identify students. 
        Applies to all dataframes.

    > term : string

        Academic period: e.g., '202580'.

    > years_to_grad : integer

        The number of years to graduation for which to calculate the graduation rate.  

    > aid_year_column : str
    
    >> default : 'AID_YEAR'
        
        Column name in the Pell table dataframe for aid year.
    
    > cohort_column : str
    
    >> default : 'Cohort Name'
        
        Column in the 'Undergraduate Retention and Graduation'
        dataframe that stores the cohort names in the format 
        '2025 Fall, First-Time, Full-Time'

    Returns
    -------
    > decimal float
        
        Graduation rate rounded to 3 decimal places. 

    Example
    -------
    > term = '202180'

    > id_column = 'ID'

    > cohort_column = 'Cohort Name'

    > years_to_grad = 4

        return 
        
            0.583
        
            The graduation rate of the 2021 Pell recipient, FED cohort. 
    #
    """
    validate_columns(df=dfp, id_column=id_column, required_cols=required_pell_columns())
    validate_columns(df=dfr, id_column=id_column, required_cols=required_cohort_columns())

    aid_year = calc_academic_year_from_term(term)
    cohort = construct_cohort(term)
    # Filter IDs by aid year and cohort
    pids = dfp.loc[dfp[aid_year_column] == aid_year, id_column].dropna()
    
    cond1 = dfr[cohort_column] == cohort
    cond2 = pd.to_numeric(dfr['Years to Graduation'].dropna(), errors='coerce') <= years_to_grad
    rids = dfr.loc[cond1 & cond2, id_column].dropna()

    n_grad = len(set(pids) & set(rids)) # number of pell graduates
    n_tot = grs_cohort_pell(dfp=dfp, dfr=dfr, id_column=id_column, term=term, 
                            aid_year_column=aid_year_column, cohort_column=cohort_column)
                            # total numer of pell feds
    
    return round(n_grad / n_tot, 3)


def second_year_retention_rate(
    dfr: pd.DataFrame,
    id_column: str,
    term: str,
    cohort_column: str = "Cohort Name"
) -> float:
    """
    # Second-year retention rate for the FED cohort of the given academic period

    Parameters
    ----------
    > dfr : pandas DataFrame
        
        Undergraduate Retention and Graduation table.

    > id_column : string
        
        The name of the column being used to identify students. 
        Applies to all dataframes.

    > term : string

        Academic period: e.g., '202580'.

    > cohort_column : str
    
    >> default : 'Cohort Name'
        
        Column in the 'Undergraduate Retention and Graduation'
        dataframe that stores the cohort names in the format 
        '2025 Fall, First-Time, Full-Time'

    Returns
    -------
    > decimal float
        
        Retention rate rounded to 3 decimal places. 

    Example
    -------
    > term = '202480'

    > id_column = 'ID'

    > cohort_column = 'Cohort Name'

        return 
        
            0.899
        
            The retention rate of the 2024 FED cohort. 
    #
    """
    validate_columns(df=dfr, id_column=id_column, required_cols=required_cohort_columns())

    retention_term = adjust_term(term=term, years=1)
    cohort = construct_cohort(term)
    cond1 = dfr[cohort_column] == cohort
    cond2 = dfr['Academic Period 2nd Fall'] == retention_term

    n_ret = sum(cond1 & cond2)
    n_tot = grs_cohort(dfr=dfr, id_column=id_column, term=term, cohort_column=cohort_column)
    
    return round(n_ret / n_tot, 3)


def second_year_retention_rate_pell(
    dfp: pd.DataFrame,
    dfr: pd.DataFrame,
    id_column: str,
    term: str,
    aid_year_column: str = "AID_YEAR",
    cohort_column: str = "Cohort Name"
) -> int:
    """
    # Second-year retention rate for the Pell + FED cohort of the given academic period

    Parameters
    ----------
    > dfp : pandas DataFrame
        
        Pell table.
    
    > dfr : pandas DataFrame
        
        Undergraduate Retention and Graduation table.

    > id_column : string
        
        The name of the column being used to identify students. 
        Applies to all dataframes.

    > term : string

        Academic period: e.g., '202580'.

    > aid_year_column : str
    
    >> default : 'AID_YEAR'
        
        Column name in the Pell table dataframe for aid year.
    
    > cohort_column : str
    
    >> default : 'Cohort Name'
        
        Column in the 'Undergraduate Retention and Graduation'
        dataframe that stores the cohort names in the format 
        '2025 Fall, First-Time, Full-Time'

    Returns
    -------
    > decimal float
        
        Retention rate rounded to 3 decimal places. 

    Example
    -------
    > term = '202480'

    > id_column = 'ID'

    > cohort_column = 'Cohort Name'

        return 
        
            0.855
        
            The retention rate of the 2024 PELL+FED cohort. 
    #
    """
    validate_columns(df=dfp, id_column=id_column, required_cols=required_pell_columns())
    validate_columns(df=dfr, id_column=id_column, required_cols=required_cohort_columns())

    aid_year = calc_academic_year_from_term(term)
    cohort = construct_cohort(term)
    # Filter IDs by aid year and cohort
    pids = dfp.loc[dfp[aid_year_column] == aid_year, id_column].dropna()
    
    retention_term = adjust_term(term=term, years=1)
    cohort = construct_cohort(term)
    cond1 = dfr[cohort_column] == cohort
    cond2 = dfr['Academic Period 2nd Fall'] == retention_term
    rids = dfr.loc[cond1 & cond2, id_column].dropna()

    n_ret = len(set(pids) & set(rids)) # number of pell graduates
    n_tot = grs_cohort_pell(dfp=dfp, dfr=dfr, id_column=id_column, term=term, 
                            aid_year_column=aid_year_column, cohort_column=cohort_column)
                            # total numer of pell feds
    
    return round(n_ret / n_tot, 3)


def total_headcount(dfe: pd.DataFrame, term: str, id_column: str) -> int:
    """
    # Calculate total full-time, degree-seeking, undergraduate enrollment headcount for the provided academic period/term.

    Parameters
    ----------
    > dfe : pandas DataFrame
        
        Census Date Enrollment table.
    
    > term : string

        Academic period: e.g., '202580'.

    > id_column : string
        
        The name of the column being used to identify students. 
        Applies to all dataframes.
    
    Returns
    -------
    > integer
        
        Total enrollment headcount. 

    Example
    -------
    > term = '202580'

    > id_column = 'ID'

        return 
        
            6939
    #
    """
    validate_columns(df=dfe, id_column=id_column, required_cols=required_enrollment_columns())

    dfe = filter_enrollment_table(dfe=dfe, term=term)

    return dfe[id_column].dropna().nunique()

