#  ------------------------
#  ----------libs----------
#  ------------------------
import curl_cffi
import json 
import pandas as pd
from numpy import where
import logging

# seting up a logger
logger = logging.getLogger(__name__)

# ---------------------------------
# ----------funcs------------------
# ---------------------------------

def get_data_json(url, path_name, headers):
    """
    Fetch data from a URL and save it to a JSON file.
    Args:
        url (str): The URL endpoint to fetch data from.
        path_name (str): The file path where the JSON data will be saved.
        headers (dict): HTTP headers to include in the request.
    Returns:
        None
    Raises:
        requests.exceptions.RequestException: If the HTTP request fails.
        IOError: If the file cannot be written.
        json.JSONDecodeError: If the response body is not valid JSON.
    Example:
        >>> get_data("https://api.example.com/data", "data-raw/milan.json", {"User-Agent": "Mozilla/5.0"})
    """

    req = curl_cffi.get(url=url, headers=headers)
    # only if the status code is OK we write to file
    if req.status_code == 200:
        with open(path_name, 'w+') as f:
            json.dump(req.json(), f)
        logging.info(f"JSON written to file")
    else:
        # print(f"Request failed with code {req.status_code}")
        logging.error(f"Request failed with code {req.status_code}")


def rep_with_space(df: pd.DataFrame, rep_dict: dict):
    """
    Replace specified substrings in DataFrame columns and optionally convert to integer.
    
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to modify.
    rep_dict : dict
        A dictionary where keys are column names and values are dicts containing:
        - 'to-replace': list of substrings to replace
        - 'to-int': conversion type ('1' for int, '0' for no conversion)
    
    Returns
    -------
    None
        Modifies the DataFrame in place.
    
    Examples
    --------
    >>> rep_dict = {'rooms': {'to-replace': [' rooms'], 'to-int': '1'}}
    >>> rep_with_space(df, rep_dict)
    """
    for col, rules in rep_dict.items():
        for word in rules.get('to-replace', []):
            df[col] = df[col].str.replace(word, '')
        if rules.get('to-int') == '1':
            df[col] = df[col].astype(int)


# ----------------------------------------
# -----------final function---------------
# ----------------------------------------

def scrape_clean():
    #  ------------------------
    #  ----- scraping part ----
    #  ------------------------
    url = "https://www.idealista.it/en/ajax/listing/georeach/milano-milano"

    # doesn't use the basic curl_cffi headers for impersonating because need a datadome cookie to scrape 
    headers = {"header-key":"header-value"}

    # TODO COMMENTED OUT SO IT DOESN'T RUN!
    # get_data_json(url, path_name='data-raw/milan.json', headers=headers)

    # ---------------------
    # ------cleaning-------
    # ---------------------
    with open('demo-project/data-raw/milan.json', 'r') as f:
        milan_json = json.load(f)

    df = pd.json_normalize(milan_json['body']['ads']) 

    # subset the dataframe for regression variables
    df = df[['adId', 'distance', 'address', 'detailUrl', 'price', 'features']]

    # splitting because requires it
    df[['rooms', 'area','amenities']] = pd.DataFrame(df['features'].to_list())
    # splitting on the whitespace before the capital letter, because difficult otherwise
    df[['floor', 'lift']] = df['amenities'].str.split(r'\s(?=[A-Z])', 
    regex=True, expand=True)

    # dictionary containing columns for cleaning 
    rep_dict = {
        'rooms': {
            'to-replace': [' rooms'],
            'to-int': '1'
        },
        'area': {
            'to-replace': [' m²'],
            'to-int': '1'
        },
        'floor': {
            'to-replace': [' floor'],
            'to-int': '0'
        }
    }

    # running the cleaning
    rep_with_space(df, rep_dict)

    # floor needs to be an int for the regression
    df['floor'] = where(df['floor']=='Ground', '0', df['floor'])

    # dictionary for cleaning the floor column - it requires multiple cleaning steps
    floor_dict = {'floor':{
        'to-replace':['st', 'nd', 'rd', 'th'],
        'to-int':'1'
    }}

    rep_with_space(df, rep_dict=floor_dict)

    # changing it to bool because better for the regression indicator
    df['lift_ind'] = where(df['lift']=='With lift', 1, 0)


    # --------------------
    # ----subset+export---
    # --------------------

    df = df[['adId', 'price', 'distance', 'rooms', 'area', 'floor', 'lift_ind']]
    df.to_csv("demo-project/results/data_clean.csv")


# if you were to run part of it here you can do it with again the same if statement:
if __name__=="__main__":
    # you set up the logging here when running the file separately so you can see what happens
    logging.basicConfig(level=logging.DEBUG, filename=f"demo-project/scrape_clean.log")
    
    # scrape_clean()