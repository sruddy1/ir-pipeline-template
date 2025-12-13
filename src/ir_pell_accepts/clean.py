import pandas as pd

def remove_leading_zeros(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    # Remove leading zeros from a given column of a dataframe and return dataframe.

        Raises ValueError() if column is not contained in df.
    
    Parameters
    ----------
    > df : pandas DataFrame
    
        Dataframe to modify.

    > column : string
        
        Name of column within dataframe. 

    Returns
    -------
    > pandas DataFrame
        
        df is returned with df[column] free of leading zeros
    #
    """
    if not column in df.columns:
        raise ValueError(f"{column} column is not present in the dataframe.")
    
    df = df.copy()
    df['ID'] = df['ID'].astype(str).str.lstrip('0')

    return df
