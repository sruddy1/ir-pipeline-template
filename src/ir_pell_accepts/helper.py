import pandas as pd


def adjust_term(term: str, years: int) -> str:
    """
    # Calculate the academic period that is a given number of years prior to the provided academic period/term.

    Parameters
    ------
    > term : string

        Academic period: e.g., '202580'.

    > years : integer
        
        How many years to subtract
    
    Returns
    -------
    > string
    
        The term in the from '202580' corresponding to the cohort whose 'years' can now
        be calculated. Ex: If the current term is 202580 then the term
        202180 can now have their 4-yr grad rate calculated. This function
        returns the term 'years' back.
    
    Example
    -------
    > term = '202580'

    > years = 4
    
        return 
        
            '202180'
    #
    """
    return "".join([str(int(term[:4]) + years), term[-2:]])


def calc_academic_year_from_term(term: str, two_digit: bool=True) -> str:
    """
    # Convert an academic period/term to its academic year.

    Parameters
    ----------
    > term : string

        Academic period: e.g., '202580'.
    
    > two_digit : boolean
    
    >> default : True

        True: function returns in the format '2526'.

        False: function returns in the format '2025-2026'.

    Returns
    -------
    > string 
    
        Academic year of the provided academic period
        
    Example
    -------
    > term = '202580'

    > two_digit = False

        return 
        
            '2526'

    > term = '202580'

    > two_digit = True

        return 
        
            '2025-2026'
    # 
    """
    year = term[:4]
    acad_year = term[2:4] + str(int(term[2:4])+1) if two_digit else "-".join([year, str(int(year) + 1)])
    return acad_year


def calc_percent(num: float, denom: float, round_to: int = 2) -> float:
    """
    # Calculate the percentage given by the two provided numbers.

    Parameters
    ----------
    > num : integer

        The numerator.
    
    > denom : integer

        The denominator.
    
    > round_to : integer
    
        The number of decimal places to keep for the percentage

    Returns
    -------
    > float 
        
        A rounded decimal percent.

    Example
    -------
    > num = 1

    > denom = 4

        return 
        
            0.25
    #
    """
    if not isinstance(num, (int, float)) or not isinstance(denom, (int, float)) or not isinstance(round_to, (int, float)):
        raise TypeError("'num', 'denom' and 'round_to' must be numeric (int or float).")
    round_to = round(abs(round_to), 0)

    return round(num/denom, round_to) 


def construct_cohort(term: str, cohort_type: str = "Fall, First-Time, Full-Time") -> str:
    """
    # Append the year of the provided term to the provided cohort type.
    
        The purpose is to match the format used by the column 'Cohort Name' contained 
        in the 'Undergraduate Retention and Graduation' file.

    Parameters
    ----------
    > term : string

        Academic period: e.g., '202580'.

    > cohort_type : string 
    
    >> default : "Fall, First-Time, Full-Time"
        
        Values from 'Cohort Type Desc' column in the 
        'Undergraduate Retention and Graduation' file. 
        In other words, 1 of the 8 cohort groups in its expanded format.
    
    Returns
    -------
    > string 
    
    Example
    -------
    > term = '202580'
    
    > cohort_type = 'Fall, First-Time, Full-Time'

        return 
        
            '2025 Fall, First-Time, Full-Time'
    #
    """
    return " ".join([term[:4], cohort_type]) 


def filter_enrollment_table(dfe: pd.DataFrame, term: str) -> pd.DataFrame:
    """
    # Filter census date enrollment table to full-time, degree-seeking undergraduates of the given academic period/term.

    Parameters
    ----------
    > dfe : pandas DataFrame
        
        Census Date Enrollment table.
    
   > term : string

        Academic period: e.g., '202580'.
    
    Returns
    -------
    > pandas Dataframe
        
        Filtered census date enrollment table 
    #
    """
    enrollment_conditions = (
        (dfe['Academic Period'] == term) &
        (dfe['Time Status'] == 'FT') &
        (dfe['Student Level'] == 'UG') &
        (dfe['Degree'] != 'Non Degree')
    )
    return dfe[enrollment_conditions]

