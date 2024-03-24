import re


def replace_string_in_df(df, term_replacements):
    """Replace whole words in a DataFrame using a dictionary of replacements."""
    for term, replacement in term_replacements.items():
        # term = r"\b" + term + r"\b"  # Add word boundaries to the term
        df.replace({term: replacement}, regex=True, inplace=True)
    return df


def replace_strings_in_string(string, term_replacements):
    """Replace whole words in a string using a dictionary of replacements."""
    for term, replacement in term_replacements.items():
        # term = r"\b" + term + r"\b"  # Add word boundaries to the term
        string = re.sub(term, replacement, string)
    return string


term_replacements = {
    re.escape("cubic meter"): r"m$^{3}$",
    re.escape("m3"): r"m$^{3}$",
    re.escape("kilogram"): "kg",
    re.escape("kgCO2eq"): "kg CO$_{2}$ eq.",
    re.escape("kg CO2 eq"): "kg CO$_{2}$ eq.",
    re.escape("kg CO2-eq"): "kg CO$_{2}$ eq.",
    re.escape("kg CO2-Eq"): "kg CO$_{2}$ eq.",
    re.escape("kilowatt hour"): "kWh",
    re.escape("Carbondioxide"): "CO$_{2}$",
    re.escape("Naturalgas"): "Natural gas",
    re.escape("square meter"): "m$^{2}$",
    re.escape("-Eq"): " eq.",
    re.escape("m2"): "m$^{2}$",
    re.escape("H+"): "H$^{+}$",
}