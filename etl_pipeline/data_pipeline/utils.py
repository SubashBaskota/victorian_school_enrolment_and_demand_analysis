#utils.py
import re
import pandas as pd

def clean_lga_name(name):
    """
    Standardises LGA names by stripping trailing council-type suffixes,
    e.g. 'Casey (C)' -> 'Casey', 'Latrobe (C) (Vic.)' -> 'Latrobe'.
    Handles nested double-parenthesis cases via a repeat-until-stable loop.
    """
    if pd.isna(name):
        return name
    cleaned = name
    while True:
        new_cleaned = re.sub(r'\s*\([^)]+\)\s*$', '', cleaned)
        if new_cleaned == cleaned:
            break
        cleaned = new_cleaned
    return cleaned.strip()