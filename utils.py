def convert_brazilian_number(value):
    """
    Convert Brazilian-formatted number string to float
    - Removes dots used as thousand separators
    - Replaces comma with dot for decimal separation
    """
    if pd.isna(value):
        return np.nan

    value = value.replace('.', '')
    value = value.replace(',', '.')
    return float(value)

