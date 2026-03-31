#  ------------------------
#  ----------libs----------
#  ------------------------
import curl_cffi
# pip install curl_cffi --upgrade
import json 
import pandas as pd
from numpy import where
import logging

#  ------------------------
#  ----- logging part ---- TODO: LATER!
#  ------------------------
# a very practical way of setting it up is to write a logging statement that only takes a separate logger if file evaluated directly. Otherwise, you want to just take over the logging from the main file.
# logger = logging.getLogger(__name__)

# if __name__ == "__main__":
#     logging.basicConfig(level=logging.DEBUG, filename='scrape-clean.log')

# generally all of this should be kinda cleaned up for when we make it a ready script 

#  ------------------------
#  ----- scraping part ----
#  ------------------------
url = "https://www.idealista.it/en/ajax/listing/georeach/milano-milano"

# doesn't use the basic curl_cffi headers for impersonating because need a datadome cookie to scrape 
headers = {
    'authority': 'www.idealista.it',
    'method': 'GET',
    'path': '/it/ajax/listing/georeach/milano-milano',
    'scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-GB,en;q=0.9',
    'cache-control': 'no-cache',
    'cookie': 'lang=it; userUUID=538e6504-263f-4bc7-849d-53e11002ad76; contact25ff0fc7-e1bb-4bf2-84a4-627c9c2ea978="{\'maxNumberContactsAllow\':10}"; cookieSearch-1=%2Fvendita-case%2Fmilano-milano%2F%3A1771922349150; uppar=false; SESSION=7eb990ed5207cfc8~25ff0fc7-e1bb-4bf2-84a4-627c9c2ea978; PARAGLIDE_LOCALE=it; didomi_token=eyJ1c2VyX2lkIjoiMTljOGVjZDYtNGMyNS02NTQzLWJkMmMtZjcyNDdjY2FlODQ1IiwiY3JlYXRlZCI6IjIwMjYtMDItMjRUMDg6Mzk6MTEuMjk4WiIsInVwZGF0ZWQiOiIyMDI2LTAyLTI0VDA4OjM5OjExLjI5OFoiLCJ2ZXJzaW9uIjpudWxsfQ==; datadome=4E9xr85MlWe3MCFzSO2LmIIxu8gNp30F0~_AOhvKePjzvx~sFJLbeTsS~rEJGtljiq_7tuJ10G5FLsWYaC6SwORdGxZqQLSMJzowukO0ZjsUPeWuABQBmF6u4wGygsUU',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.idealista.it/vendita-case/milano-milano/',
    'sec-ch-device-memory': '8',
    'sec-ch-ua': '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
    'sec-ch-ua-arch': '"x86"',
    'sec-ch-ua-full-version-list': '"Not:A-Brand";v="99.0.0.0", "Microsoft Edge";v="145.0.3800.70", "Chromium";v="145.0.7632.110"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0'
}


req = curl_cffi.get(url=url, headers=headers)

with open('../data-raw/milan.json', 'w+') as f:
    json.dump(req.json(), f)

# important: when using the interactive session, use the '..' in front of folder, because the pwd is different (unless you change it) 

# ----------------
#  TODO LATER!
# ----------------

# alternative version where we use the function
# def get_data_json(url, path_name, headers):
#     """
#     Fetch data from a URL and save it to a JSON file.
#     Args:
#         url (str): The URL endpoint to fetch data from.
#         path_name (str): The file path where the JSON data will be saved.
#         headers (dict): HTTP headers to include in the request.
#     Returns:
#         None
#     Raises:
#         requests.exceptions.RequestException: If the HTTP request fails.
#         IOError: If the file cannot be written.
#         json.JSONDecodeError: If the response body is not valid JSON.
#     Example:
#         >>> get_data("https://api.example.com/data", "data-raw/milan.json", {"User-Agent": "Mozilla/5.0"})
#     """

#     req = curl_cffi.get(url=url, headers=headers)
#     # only if the status code is OK we write to file
#     if req.status_code == 200:
#         with open(path_name, 'w+') as f:
#             json.dump(req.json(), f)
#         logging.info(f"JSON written to file")
#     else:
#         # print(f"Request failed with code {req.status_code}")
#         logging.error(f"Request failed with code {req.status_code}")



# get_data_json(url=url, path_name='demo-project/data-raw/milan.json', headers=headers)


# ---------------------
# ------cleaning-------
# ---------------------

# df = pd.read_json('../data-raw/milan.json')
# doesn't use pandas since need to subset it for ads

with open('../data-raw/milan.json', 'r') as f:
    milan_json = json.load(f)

# TODO Show the interactive mode!
# what i tried at first and didn't work
# df = pd.json_normalize(milan_json) 

# what works
df = pd.json_normalize(milan_json['body']['ads']) 


# subset the dataframe for regression variables
df = df[['adId', 'distance', 'address', 'detailUrl', 'price', 'features']]

# splitting because requires it
df[['rooms', 'area','amenities']] = pd.DataFrame(df['features'].to_list())
# splitting on the whitespace before the capital letter, because difficult otherwise
df[['floor', 'lift']] = df['amenities'].str.split(r'\s(?=[A-Z])', 
regex=True, expand=True)

# cleaning columns to adjust type for the regression later
# these are not used but left here for exposition of how repeated code would look like
# df['rooms'] = df['rooms'].str.replace(' rooms', '').astype(int)
# df['area'] = df['area'].str.replace(' m²', '').astype(int)
# df['floor'] = df['rooms'].str.replace(' floor', '')

# -------
#  making a cleaning function here
# -------


# We also write a pretty docstring for it with ai
def rep_with_space(df: pd.DataFrame, rep_dict: dict):
    """
    Replace specified substrings in DataFrame columns and optionally convert to integer.
    Processes a DataFrame by applying string replacements and type conversions based on 
    a configuration dictionary. For each column specified in the rules, removes specified 
    words/substrings and optionally converts the column to integer type.
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be modified in-place. Columns referenced in rep_dict must contain 
        string or object-type data.
    rep_dict : dict
        A dictionary mapping column names to replacement rules. Each value is a dictionary 
        with the following optional keys:
        - 'to-replace' (list): List of substrings to remove from the column values. 
          If not provided or empty, no replacements are performed.
        - 'to-int' (str): If set to '1', converts the column to integer type after 
          replacements. Any other value is ignored.
    Returns
    -------
    None
        Modifies the DataFrame in-place. No value is returned.
    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'price': ['$100.00', '$200.50'], 'quantity': ['5 units', '10 units']})
    >>> rules = {
    ...     'price': {'to-replace': ['$', '.00'], 'to-int': '0'},
    ...     'quantity': {'to-replace': [' units'], 'to-int': '1'}
    ... }
    >>> rep_with_space(df, rules)
    >>> df
      price  quantity
    0   100          5
    1   200         10
    Notes
    -----
    - Modifications are applied in-place to the input DataFrame.
    - Replacements are performed sequentially for each word in 'to-replace'.
    - String replacements occur before type conversion.
    - Column must contain string-convertible data for type conversion to succeed.
    """

    for col, rules in rep_dict.items():
        for word in rules.get('to-replace', []):
            df[col] = df[col].str.replace(word, '')
        if rules.get('to-int') == '1':
            df[col] = df[col].astype(int)

# now we should move this whole thing to to the top to improve readibility


# we make a dictionary of this type for it:
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

# re use the function again because needs a second step
floor_dict = {'floor':{
    'to-replace':['st', 'nd', 'rd', 'th'],
    'to-int':'1'
}}

rep_with_space(df, rep_dict=floor_dict)

# boolean is better for a lift indicator
df['lift_ind'] = where(df['lift']=='With lift', 1, 0)


# --------------------
# ----subset+export---
# --------------------

df = df[['adId', 'price', 'distance', 'rooms', 'area', 'floor', 'lift_ind']]

df.to_csv("../results/data_clean.csv")

# TODO: git time