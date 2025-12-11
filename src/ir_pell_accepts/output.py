from pathlib import Path
from datetime import date
from importlib.metadata import version
import pandas as pd
from ir_pell_accepts.checks import validate_filename, validate_extension
from ir_pell_accepts.helper import adjust_term

def construct_results_filename(file: Path, append_today: bool = True, append_version: bool = True) -> Path:
    """
    Create the file name for the results file and append today's date and package version by default.

    Params
    ------
    file : Path object from pathlib
        The file name including extension, not a full path, just the name.
    append_today : bool
        Add today's date to the file name (e.g. 11-25-2025)
    append_version : bool
        Append the version of the python package used (e.g. v0.1.0)
    """
    file = validate_filename(file)
    todays_date = date.today().strftime("%Y-%m-%d") if append_today else None
    pkg_version = "v" + version("ir_pell_accepts") if append_version else None

    # Remove None's/blanks
    parts = [file.stem, todays_date, pkg_version]
    parts = [p for p in parts if p]

    return Path("_".join(parts) + file.suffix)


def contruct_results_df(
    term: str,
    cohort_first: float,
    pell_first: float,
    cohort_first_grad_4: float,
    pell_first_grad_4: float,
    cohort_first_grad_6: float,
    pell_first_grad_6: float,
    cohort_first_retention: float,
    pell_first_retention: float,
    headcount_nottr: float,
    pell_nottr: float,
    headcount_transfer: float,
    transfer_pell: float,
    headcount: float,
    pell_first_pct: float,
    pell_nottr_pct: float,
    pell_transfer_pct: float
) -> pd.DataFrame:
    
    grad_4_year = adjust_term(term=term, years=-4)[:4]
    grad_6_year = adjust_term(term=term, years=-6)[:4]
    retention_cohort_term = adjust_term(term=term, years=-1)[:4]
    
    results = [{
        "grs_cohort": cohort_first,
        "grs_cohort_pell": pell_first,
        "_".join(["grs_cohort_grad_4yr", grad_4_year]): cohort_first_grad_4,
        "_".join(["grs_cohort_pell_grad_4yr", grad_4_year]): pell_first_grad_4,
        "_".join(["grs_cohort_grad_6yr", grad_6_year]): cohort_first_grad_6,
        "_".join(["grs_cohort_pell_grad_6yr", grad_6_year]): pell_first_grad_6,
        "_".join(["retention_rate", retention_cohort_term]): cohort_first_retention,
        "_".join(["retention_rate_pell", retention_cohort_term]): pell_first_retention,
        "fall_enrollment": headcount_nottr,
        "fall_enrollment_pell": pell_nottr,
        "fall_transfer_enrollment": headcount_transfer,
        "fall_transfer_enroll_pell": transfer_pell,
        "total_enrollment": headcount,
        "pell_first_pct": pell_first_pct,
        "pell_pct": pell_nottr_pct,
        "pell_transfer_pct": pell_transfer_pct 
    }]

    return pd.DataFrame(results)


def output_results(df: pd.DataFrame, file_path: Path, append_today: bool = True, append_version: bool = True) -> None:
    """
    Output results to excel, csv, or tab/.txt
    """
    file = file_path.name
    if not file:
        raise ValueError(f"file_path must have a filename: {file_path}")
    
    file = construct_results_filename(file, append_today=append_today, append_version=append_version)
    
    outfile = file_path.parent / file
    ext = validate_extension(outfile.suffix)

    if ext == ".xlsx":
        df.to_excel(outfile, index=False)
    if ext == ".csv":
        df.to_csv(outfile, index=False)
    if ext == ".txt":
        df.to_csv(outfile, index=False, sep="\t")
