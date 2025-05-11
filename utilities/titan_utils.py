# titan_utils.py

import pandas as pd

def save_to_excel(predictions, filename):
    """
    Save the list of predictions into an Excel (.xlsx) file.
    """
    df = pd.DataFrame(predictions)
    df.to_excel(filename, index=False)
