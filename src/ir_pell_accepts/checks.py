from pathlib import Path
import pandas as pd


def required_cohort_columns() -> set[str]:
    """
    # Return the column names in the 'Undergraduate Retention and Graduation' file that are required for the ATI-Kessler report.

    Parameters
    ----------
        Does not take parameters.

    Returns
    -------
    > set of strings

        {'Cohort Name'}
    #
    """
    return {'Cohort Name'}
    

def required_enrollment_columns() -> set[str]:
    """
    # Return the column names in the 'Census Date Enrollment' file that are required for the ATI-Kessler report.

    Parameters
    ----------
        Does not take parameters.

    Returns
    -------
    > set of strings

        {'Academic Period', 'Time Status', 'Student Level', 'Degree'}
    #
    """
    return {'Academic Period', 'Time Status', 'Student Level', 'Degree'}


def required_pell_columns() -> set[str]:
    """
    # Return the column names in the Pell Recipient file that are required for the ATI-Kessler report.

    Parameters
    ----------
        Does not take parameters.

    Returns
    -------
    > set of strings

        {'AID_YEAR'}
    #
    """
    return {'AID_YEAR'}


def validate_columns(df: pd.DataFrame, id_column: str, required_cols: set[str] | None = None) -> None:
    """
    # Check that the columns of a given dataframe contain the columns required for the project. 
    
        Raises a ValueError() if the columns provided are not contained
        inside the dataframe, otherwise returns nothing.

    Parameters
    ----------
    > df : pandas dataframe

        The dataframe of the table.

    > id_column : string
        
        The name of the column being used to identify students.

    > required_cols : set of strings {'column 1', 'column 2'}

    >> default : None

        An additional set of column names.
    
    Returns
    -------
    > None
    
        Exits quietly if checks pass, otherwise
        raises a ValueError()
    
    Example
    -------
    > df = dataframe that contains 'ID' and 'Cohort Name'

    > id_column = 'ID'

    > required_cols = {'Cohort Name'}
    
        return 
        
            None

    > df = dataframe that DOES NOT contain 'ID'
    
    > id_column = 'ID'

    > required_cols = None
    
        raise
        
            ValueError: Missing required columns {'ID'} 
    #
    """
    required_cols = set(required_cols) 
    required_cols.add(id_column)

    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    return None


def validate_extension(ext: str) -> str:
    """
    # Check that an extension of a file name is a valid type. 
    
        Raises a ValueError() if the extension is not one of 
        .txt/.csv/.xlsx. Otherwise, it returns the extension
        that was provided.

    Parameters
    ----------
    > ext : str

        Must contain a '.', e.g. '.xlsx'

    Returns
    -------
    > string

        If extension is valid, the extension provided
        is returned as a string. Otherwise, a ValueError()
        is raised.
    
    Example
    -------
    > ext = '.xlsx'

        return 
        
            '.xlsx'
    
    > ext = '.gibberish'

        raise 
    
            ValueError() 
    #
    """
    allowed = [".xlsx", ".csv", ".txt"]

    if ext not in allowed:
        raise ValueError(f"results file must have a valid extension: {allowed}")

    return ext


def validate_filename(path_arg: str | Path) -> Path:
    """
    # Validate that the provided path is a path to a file, not just a directory. Then, validate its extension.

        If checks pass, return the provided path as a Path object.
        Otherwise, raise a ValueError()

    Parameters
    ----------
    > path_arg : string or Path object

        Path to an actual file with an appropriate extension (csv/txt/xlsx)

    Returns
    -------
    > Path object

        Path(path_arg) if checks pass. Otherwise, raise
        a ValueError().

    Example
    -------
    > path_arg = '/c/Users/sruddy1/my_file.xlsx'

        return 
        
            Path('/c/Users/sruddy1/my_file.xlsx')

    > path_arg = r'C:\\Users\\sruddy1\\my_file.xlsx'

        return 
        
            Path(r'C:\\Users\\sruddy1\\my_file.xlsx')

    > path_arg = '/c/Users/sruddy1'

        raise 
    
            ValueError()
    #
    """
    p = Path(path_arg)

    # 1. Check: No directory components (only a filename)
    if p.parent != Path("."):
        raise ValueError(f"Argument must be a filename, not a path: {path_arg}")

    # 2. Check: It must have a suffix / extension
    if p.suffix == "":
        raise ValueError(f"Filename must have an extension: {path_arg}")

    return p



