from pathlib import Path

import pandas as pd


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

