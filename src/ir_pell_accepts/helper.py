
def calc_academic_year_from_term(term: str) -> str:
    """
    Params
    ------
    term : str
        eg. "202580"
    
    Returns
    -------
        String in the form "2526", representing the academic year of the given term.
    """
    return term[2:4] + str(int(term[2:4])+1)


def construct_cohort(term: str, cohort_type: str = "Fall, First-Time, Full-Time") -> str:
    """
    Params
    ------
    term : str
        eg. "202580"
    cohort_type : str
        aligns to retention file, column 'Cohort Name'
    
    Returns
    -------
        String in the form "2025 Fall, First-Time, Full-Time", 
        representing the academic year of the given term, restricted to the 
        written cohort type.
    """
    return term[0:4] + " " + cohort_type 


def calc_percent(num: float, denom: float, round_to: int = 2) -> float:
    """
    Return percentage round((num/denom)*100, round_to)

    Params
    ------
    num : integer
    denom : integer
    round_to : integer
        The number of decimal places to keep for the percentage
    """
    if not isinstance(num, (int, float)) or not isinstance(denom, (int, float)) or not isinstance(round_to, (int, float)):
        raise TypeError("'num', 'denom' and 'round_to' must be numeric (int or float).")
    round_to = round(abs(round_to), 0)

    return round((num/denom)*100, round_to) 

def adjust_term(term: str, years: int) -> str:
    """
    Params
    ------
    term : str
        eg. "202580"
    years : int
        student took no more than 'years_to_grad' to graduate.
    
    Returns
    -------
    str
        The term corresponding to the cohort whose 'years_to_grad' can now
        be calculated. Ex: If the current term is 202580 then the term
        202180 can now have their 4-yr grad rate calculated. This function
        returns the term 'years_to_grad' back.
    """
    return "".join([str(int(term[:4]) + years), term[-2:]])

