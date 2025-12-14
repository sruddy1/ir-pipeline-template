from pathlib import Path
from datetime import date
from importlib.metadata import version
import pandas as pd
from ir_pell_accepts.checks import validate_filename, validate_extension
from ir_pell_accepts.helper import adjust_term


def construct_results_filename(file: str | Path, append_today: bool = True, append_version: bool = True) -> Path:
    """
    # Modifies the file name for the results file and returns it as a Path object. 
        
        (default) Optionally appends today's date and 
        pipeline package version.
    
    Parameters
    ----------
    > file : string or Path object
    
        The file name including extension. Do not include its path.

    > append_today : boolean (True/False)

    >> default = True
        
        Append today's date to the file name in the format mm-dd-yyyy

    > append_version : boolean (True/False)

    >> default = True
        
        Append the version of the pipeline python package used to the file name, e.g. 'v0-1-0'

    Returns
    -------
    > Path object
    
        A modified file name as a Path object.

    Example
    -------
    > file = 'my_file.xlsx'

    > append_today = True

    > append_version = True

        return 
            
            'my_file_12-13-2025_v0-3-2.xlsx'
            
    #
    """
    file = validate_filename(file)
    todays_date = date.today().strftime("%Y-%m-%d") if append_today else None
    pkg_version = "".join(["v", version("ir_pell_accepts").replace(".", "-")]) if append_version else None

    # Remove None's/blanks
    parts = [file.stem, todays_date, pkg_version]
    parts = [p for p in parts if p]

    return Path("_".join(parts) + file.suffix)


def infer_and_read_file(file: str | Path) -> pd.DataFrame:
    """
    # Infers file type and reads into a pandas DataFrame.

        All columns are converted to strings. 

        Supported file types: .xlsx, .csv, and .txt

        Raises FileNotFoundError() if file does not exist
        
        Raises ValueError() if not one of the supported file types.
    
    Parameters
    ----------
    > file : string or Path object
    
        Path to file.

        Ex: '/c/Users/sruddy1/my_file.xlsx'
        
        Ex: r'C:\\Users\\sruddy1\\my_file.xlsx'

        Ex: Path('/c/Users/sruddy1/my_file.xlsx')

        Ex: Path(r'C:\\Users\\sruddy1\\my_file.xlsx')

    Returns
    -------
    > pandas DataFrame
    
        The loaded data with all columns converted to strings.
    #
    """
    allowed = {'.xlsx', '.csv', '.txt'}

    path = Path(file)

    if not path.exists():
        raise FileNotFoundError(f'Input file does not exist: {path}')

    ext = path.suffix.lower()

    if ext == '.xlsx':
        out = pd.read_excel(path, dtype=str)
    elif ext == '.csv':
        out = pd.read_csv(path, dtype=str)
    elif ext == '.txt':
        out = pd.read_csv(path, dtype=str, sep='\t')
    else:
        raise ValueError(f'Unsupported file type: {ext}. Allowed values: {allowed}')

    return out


def output_results(df: pd.DataFrame, file_path: Path, append_today: bool = True, append_version: bool = True) -> None:
    """
    # Output results to the provided file.
        
        Infers file type from file name.
        Allowed file types: .csv, .xlsx, .txt

        If .xlsx, adds or overwrites an existing sheet
        called 'Python Output'.
    
    Parameters
    ----------
    > df : pandas DataFrame

        A dataframe to write into a file.
    
    > file_path : string or Path object
    
        A full file path and file name including extension.

    > append_today : boolean (True/False)

    >> default = True
        
        Append today's date to the file name in the format mm-dd-yyyy

    > append_version : boolean (True/False)

    >> default = True
        
        Append the version of the pipeline python package used to the file name, e.g. 'v0-1-0'

    Returns
    -------
    > None
    
        Nothing is returned. Instead, a file is created or modified with 
        the output of the dataframe.

    Example
    -------
    > file_path = '/c/Users/sruddy1/my_file.xlsx'

    > append_today = True

    > append_version = True

        return  
            
            write df to a sheet called 'Python Output' to 
            '/c/Users/sruddy1/my_file_12-13-2025_v0-3-2.xlsx'
    #
    """
    file = file_path.name
    if not file:
        raise ValueError(f"file_path must have a filename: {file_path}")
    
    file = construct_results_filename(file, append_today=append_today, append_version=append_version)
    
    outfile = file_path.parent / file
    ext = validate_extension(outfile.suffix)

    if ext == ".xlsx":
        if outfile.exists():
            with pd.ExcelWriter(
                outfile,
                engine="openpyxl",
                mode="a",
                if_sheet_exists="replace"
            ) as writer:
            
                df.to_excel(writer, sheet_name="Python Output", index=False)
        else:
            df.to_excel(outfile, index=False)
    if ext == ".csv":
        df.to_csv(outfile, index=False)
    if ext == ".txt":
        df.to_csv(outfile, index=False, sep="\t")

    return None

