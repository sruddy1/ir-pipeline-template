import pandas as pd
from ir_pell_accepts.helper import calc_academic_year_from_term, construct_cohort, adjust_term
from ir_pell_accepts.checks import validate_pell_columns, validate_cohort_columns, validate_enrollment_columns

def grs_cohort_pell(
    dfp: pd.DataFrame,
    dfr: pd.DataFrame,
    id_column: str,
    term: str,
    aid_year_column: str = "AID_YEAR",
    cohort_column: str = "Cohort Name"
) -> int:
    """
    Calculate the number of Pell recipients for the given aid year and cohort type.

    Parameters
    ----------
    dfp : pandas.DataFrame
        Pell awards dataframe.
    dfr : pandas.DataFrame
        Retention / cohort dataframe.
    id_column : str
        Column to use for student IDs; must exist in both dataframes (e.g., "ID").
    term : str
        Term e.g. "202580".
    aid_year_column : str, default "AID_YEAR"
        Column in the Pell dataframe that stores aid year values.
    cohort_column : str, default "Cohort Name"
        Column in the retention dataframe that stores cohort names.

    Returns
    -------
    int
        The number of students who are both Pell recipients in the given aid year
        and cohort.

    Raises
    ------
    ValueError
        If any of the required column names are not present in their respective dataframes.
    """
    validate_pell_columns(df=dfp, id_column=id_column)
    validate_cohort_columns(df=dfr, id_column=id_column)

    aid_year = calc_academic_year_from_term(term)
    cohort = construct_cohort(term)
    # Filter IDs by aid year and cohort
    pids = dfp.loc[dfp[aid_year_column] == aid_year, id_column].dropna()
    rids = dfr.loc[dfr[cohort_column] == cohort, id_column].dropna()

    # Return overlap size
    return len(set(pids) & set(rids))


def grs_cohort(
    dfr: pd.DataFrame,
    id_column: str,
    term: str,
    cohort_column: str = "Cohort Name"
) -> int:
    """
    Calculate the total size of the provided cohort.

    Parameters
    ----------
    dfr : pandas.DataFrame
        Retention / cohort dataframe.
    id_column : str
        Column to use for student IDs; must exist in both dataframes (e.g., "ID").
    term : str
        Term e.g. "202580".
    cohort_column : str, default "Cohort Name"
        Column in the retention dataframe that stores cohort names.

    Returns
    -------
    int
        The number of students in the provided cohort.

    Raises
    ------
    ValueError
        If any of the required column names are not present in their respective dataframes.
    """
    validate_cohort_columns(df=dfr, id_column=id_column)

    cohort = construct_cohort(term)
    return sum(dfr[cohort_column] == cohort)


def filter_enrollment_table(dfe: pd.DataFrame, term: str) -> pd.DataFrame:
    enrollment_conditions = (
        (dfe['Academic Period'] == term) &
        (dfe['Time Status'] == 'FT') &
        (dfe['Student Level'] == 'UG') &
        (dfe['Degree'] != 'Non Degree')
    )
    return dfe[enrollment_conditions]


def total_headcount(dfe: pd.DataFrame, term: str, id_column: str) -> int:
    """
    Calculates enrollment headcount in the provided academic term for full-time, undergrad, degree-seeking students.

    Parameters
    ----------
    dfe : pandas.DataFrame
        The census data enrollment dataframe.
    term : str
        The term in which to calculate enrollment. (e.g., "202580").
    id_column: str
        The name of the id_column to identify unique students. (e.g., "ID").
    
    Returns
    -------
    int
        Returns the enrollment headcount for full-time, undergrad, degree-seeking students in the provide academic term.

    Raises
    ------
    ValueError
        If any of the required columns are not present in df.
    """
    validate_enrollment_columns(df=dfe, id_column=id_column)

    dfe = filter_enrollment_table(dfe=dfe, term=term)

    return dfe[id_column].dropna().nunique()


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
    Term headcounts for full-time, degree-seeking undergrads.

    Headcount Options
    -----------------
    pell = False and transfer = False
        excludes incoming transfer students
    pell = True and transfer = False
        includes pell recipients and excludes incoming transfer students
    pell = False and transfer = True
        includes only incoming transfer students
    pell = True and transfer = True
        incoming transfer students that are also pell recipients

    Parameters
    ----------
    dfp : pandas.DataFrame
        Census Date Enrollment dataframe.
    dfe : pandas.DataFrame
        Census Date Enrollment dataframe.
    dfr : pandas.DataFrame
        Retention / cohort dataframe.
    id_column : str
        Column to use for student IDs; must exist in both dataframes (e.g., "ID").
    term: str
        Academic term (e.g. "202580")
    pell : bool
        If True, restrict to just pell recipients
    transfer: bool
        If True, include incoming transfer students, otherwise exclude them. 
        
    Returns
    -------
    int
        The number of total first-time students enrolled in the given term.

    Raises
    ------
    ValueError
        If any of the required column names are not present in their respective dataframes.
    """
    validate_pell_columns(df=dfp, id_column=id_column)
    validate_cohort_columns(df=dfr, id_column=id_column)
    validate_enrollment_columns(df=dfe, id_column=id_column)

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

def grs_cohort_grad(
    dfr: pd.DataFrame,
    id_column: str,
    term: str,
    years_to_grad: int,
    cohort_column: str = "Cohort Name"
) -> float:
    """
    N-year FED graduation rate

    Parameters
    ----------
    dfr : pandas.DataFrame
        Retention / cohort dataframe.
    id_column : str
        Column to use for student IDs; must exist in both dataframes (e.g., "ID").
    term : str
        Term e.g. "202580".
    years_to_grad : int
        student took no more than 'years_to_grad' to graduate.
    cohort_column : str, default "Cohort Name"
        Column in the retention dataframe that stores cohort names.

    Returns
    -------
    float
        returns decimal proportion of grad rate, rounded to 3 decimal places.

    Raises
    ------
    ValueError
        If any of the required column names are not present in their respective dataframes.
    """ 
    validate_cohort_columns(df=dfr, id_column=id_column)

    cohort = construct_cohort(term)
    cond1 = dfr[cohort_column] == cohort
    cond2 = pd.to_numeric(dfr['Years to Graduation'].dropna(), errors='coerce') <= years_to_grad

    n_grad = sum(cond1 & cond2)
    n_tot = grs_cohort(dfr=dfr, id_column=id_column, term=term, cohort_column=cohort_column)
    
    return round(n_grad / n_tot, 3)


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
    N-year Pell-recipient FED graduation rate among all Pell-recipient FED students.

    Parameters
    ----------
    dfp : pandas.DataFrame
        Pell awards dataframe.
    dfr : pandas.DataFrame
        Retention / cohort dataframe.
    id_column : str
        Column to use for student IDs; must exist in both dataframes (e.g., "ID").
    term : str
        Term e.g. "202580".
    years_to_grad : int
        student took no more than 'years_to_grad' to graduate.
    aid_year_column : str, default "AID_YEAR"
        Column in the Pell dataframe that stores aid year values.
    cohort_column : str, default "Cohort Name"
        Column in the retention dataframe that stores cohort names.

    Returns
    -------
    float
        returns decimal proportion of grad rate, rounded to 3 decimal places.

    Raises
    ------
    ValueError
        If any of the required column names are not present in their respective dataframes.
    """
    validate_pell_columns(df=dfp, id_column=id_column)
    validate_cohort_columns(df=dfr, id_column=id_column)

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
    Second year retention rate for FED students

    Parameters
    ----------
    dfr : pandas.DataFrame
        Retention / cohort dataframe.
    id_column : str
        Column to use for student IDs; must exist in both dataframes (e.g., "ID").
    term : str
        cohort term for which second year retainment is calculated
    cohort_column : str, default "Cohort Name"
        Column in the retention dataframe that stores cohort names.

    Returns
    -------
    float
        returns decimal proportion of retention rate, rounded to 3 decimal places.

    Raises
    ------
    ValueError
        If any of the required column names are not present in their respective dataframes.
    """ 
    validate_cohort_columns(df=dfr, id_column=id_column)

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
    Second year retention reate for Pell-recipient FED among all Pell-recipient FED students.

    Parameters
    ----------
    dfp : pandas.DataFrame
        Pell awards dataframe.
    dfr : pandas.DataFrame
        Retention / cohort dataframe.
    id_column : str
        Column to use for student IDs; must exist in both dataframes (e.g., "ID").
    term : str
        cohort term for which retention is calculated
    aid_year_column : str, default "AID_YEAR"
        Column in the Pell dataframe that stores aid year values.
    cohort_column : str, default "Cohort Name"
        Column in the retention dataframe that stores cohort names.

    Returns
    -------
    float
        returns decimal proportion of retention rate, rounded to 3 decimal places.

    Raises
    ------
    ValueError
        If any of the required column names are not present in their respective dataframes.
    """
    validate_pell_columns(df=dfp, id_column=id_column)
    validate_cohort_columns(df=dfr, id_column=id_column)

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
