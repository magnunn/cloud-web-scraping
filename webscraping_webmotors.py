# ======================================================================================================================
# IMPORTS
# ======================================================================================================================
import numpy as np
import pandas as pd
import pymysql
import re
import requests
import warnings

from bs4 import BeautifulSoup
from configparser import ConfigParser
from datetime import datetime
from sqlalchemy import create_engine

warnings.filterwarnings("ignore")

# ======================================================================================================================
# CONFIG FILE
# ======================================================================================================================
config = ConfigParser()
config.read("config.ini")

# WEB ELEMENTS FOR SCRAPING
main_url = config["WEB_SITE_ELEMENTS_BY_CLASS"]["main_url"]
results_number_webclass = config["WEB_SITE_ELEMENTS_BY_CLASS"]["results_num"]
url_id_webclass = config["WEB_SITE_ELEMENTS_BY_CLASS"]["url_id"]
price_webclass = config["WEB_SITE_ELEMENTS_BY_CLASS"]["price"]
desc_webclass = config["WEB_SITE_ELEMENTS_BY_CLASS"]["desc"]
features_webclass = config["WEB_SITE_ELEMENTS_BY_CLASS"]["features"]
accessories_webclass = config["WEB_SITE_ELEMENTS_BY_CLASS"]["accessories"]
advertiser_webclass = config["WEB_SITE_ELEMENTS_BY_CLASS"]["advertiser"]
location_webclass = config["WEB_SITE_ELEMENTS_BY_CLASS"]["location"]
photo_num_webclass = config["WEB_SITE_ELEMENTS_BY_CLASS"]["photo_num"]
results_per_page = int(config["WEB_SITE_ELEMENTS_BY_CLASS"]["page_results"])

# AWS DB
host_ = config["AWS_RDS"]["host"]
user_ = config["AWS_RDS"]["user"]
pass_ = config["AWS_RDS"]["pass"]
port_ = config["AWS_RDS"]["port"]
identifier_ = config["AWS_RDS"]["identifier"]
table_ = config["AWS_RDS"]["table"]


# ======================================================================================================================
# HELPER FUNCTIONS
# ======================================================================================================================
# Creating a dictdictionary with Product ID as the key and url as the value


def mapping_ads(url_id_webclass):
    """Navigate every result page getting URL and ID for each add on them

    :param str url_id_webclass: Class of html element which contains product's URL and ID
    :return dict catalog: Relation with every ad URL and ID
    """

    catalog = {}

    # Looping throw all results on each of results pages
    for page in range(pages_num):

        current_url = (
            "https://sp.olx.com.br/sao-paulo-e-regiao/zona-leste/autos-e-pecas/carros-vans-e-utilitarios/gm"
            "-chevrolet/onix?o={}&re=39".format(page + 1)
        )
        page_current = requests.get(current_url, headers=headers)
        soup_current = BeautifulSoup(page_current.text, "html.parser")
        # Listing all products containers on each page
        products = soup_current.find_all("a", class_=url_id_webclass)

        # Geting ID and URL of all ads in the page
        for product in range(len(products)):
            catalog[products[product]["data-lurker_list_id"]] = products[product][
                "href"
            ]

    return catalog


def get_timestamp():
    """Returns the system's timestamp

    :return float ts: Timestamp from the moment this function has been executed
    """
    dt = datetime.now()
    ts = datetime.timestamp(dt)

    return ts


def collect_ad_details(
    catalog,
    price_webclass,
    desc_webclass,
    features_webclass,
    accessories_webclass,
    advertiser_webclass,
    location_webclass,
    photo_num_webclass,
    get_timestamp,
):
    """Loop accessing every ad extracting their data

    :param dict catalog: Relation with every ad URL and ID
    :param str price_webclass: class of html element which contains ad's price
    :param str desc_webclass: class of html element which contains ad's description
    :param str features_webclass: class of html element which contains some ad's fetures
    :param str accessories_webclass: class of html element which contains ad's accessories
    :param str advertiser_webclass: class of html element which contains ad's advertiser type
    :param str location_webclass: class of html element which contains ad's location
    :param str photo_num_webclass: class of html elements which contains ad's pictures
    :param function get_timestamp: function to get current time stamp
    :return pd.Dataframe catalog_df: consolidating every ad's features and timestamp from its extraction
    """

    # Creating an empty dataframe to be filled with details from each advertisement
    catalog_df = pd.DataFrame()

    # Loop accessing with car page and extract their data
    for product in range(len(catalog)):
        product_page = requests.get(list(catalog.values())[product], headers=headers)
        soup_prod = BeautifulSoup(product_page.text, "html.parser")

        """Sometimes the data is unpatterned, not having some basic info like price and causing error on 
        '.text.stripe()' function, therefore we are using try/except structure. Losing this unpatterned data don't 
        seems to be a problem, once on (07/23/2022 from 623 results only 1 was an exception)"""
        try:
            price = soup_prod.find("h2", class_=price_webclass).text.strip()
            description = soup_prod.find("h1", class_=desc_webclass).text.strip()
            features = soup_prod.find_all("div", class_=features_webclass)
            accessories = soup_prod.find_all("span", class_=accessories_webclass)
            advertiser = soup_prod.find_all("span", class_=advertiser_webclass)
            location = soup_prod.find_all("dd", class_=location_webclass)[
                2
            ].text.strip()
            photo_num = len(soup_prod.find_all("img", class_=photo_num_webclass)) - 1

            # If the html element that describes the advertiser is a store is not empty, then the result is True
            if advertiser:
                advertiser = "store"
            else:
                advertiser = "person"

            # Creates a list with every accessory
            accessories_list = []
            for accessory in range(len(accessories)):
                accessories_list.append(accessories[accessory].text.strip())
            # Converting list to string (it will be easier to deal with SQL)
            accessories_string = ";".join(accessories_list)

            # Create a dictionary with all car feartures within the main block of information
            features_dict = {}
            for feature in range(len(features)):
                features_dict[features[feature].findChildren()[0].text.strip()] = (
                    features[feature].findChildren()[1].text.strip()
                )

            # Create a dictionary for each advertisement with its features
            prod_dict = {
                "id": list(catalog.keys())[product],
                "url": list(catalog.values())[product],
                "timestamp": get_timestamp(),
                "description": description,
                "price": price,
                "location": location,
                "accessories": accessories_string,
                "photo_num": photo_num,
                "advertiser_type": advertiser,
            }
            # Add to the main product data the data stored data on features_dict
            prod_dict.update(features_dict)
            print("ok-" + str(product))

            # Append to the final dictionary each advertisement ID as key and its features as value within a dictionary
            catalog_df = catalog_df.append(prod_dict, ignore_index=True)

        except:
            print("error" + str(product))
            pass

    return catalog_df


def upload_aws(host_, user_, pass_, table_, catalog_df):
    """Uploads ads's feautures to an AWS SQL db

    :param str host_: host of db
    :param str user_: user of db
    :param str pass_: password of db
    :param str table_: table identification
    :param pd.DataFrame catalog_df: ads's features
    """
    # Connecting
    conn = pymysql.connect(host=host_, user=user_, password=pass_, db=table_)

    # Instantiating sqlalchemy engine
    engine = create_engine(f"mysql+pymysql://admin:{pass_}@{host_}/{table_}")

    # Uploading dataframe with ads to DB
    catalog_df.to_sql(table_, engine, if_exists="append", index=False)
    conn.commit()

    # Closing connection
    conn.close()

    return None


# ======================================================================================================================
# WEB SCRAPING
# ======================================================================================================================
# *Attention! The website has a limitator of 100 result pages, so avoid using a too open filters
if __name__ == "__main__":
    # Instantiating BeautifulSoup
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/50.0.2661.102 Safari/537.36"
    }
    page_init = requests.get(main_url, headers=headers)
    soup_init = BeautifulSoup(page_init.text, "html.parser")

    # This is the of results from the search, appling regex to get its number
    results_num_raw = soup_init.find_all("span", class_=results_number_webclass)
    results_num_regex = "(\d+) resultados"
    results_num = int(re.search(results_num_regex, str(results_num_raw)).group(1))

    # Calculating how many results pages are there
    pages_num = int(np.ceil((results_num / results_per_page)))

    # Mapping every ad
    catalog = mapping_ads(url_id_webclass)

    print(len(catalog))

    # Getting ads features
    catalog_df = collect_ad_details(
        catalog,
        price_webclass,
        desc_webclass,
        features_webclass,
        accessories_webclass,
        advertiser_webclass,
        location_webclass,
        photo_num_webclass,
        get_timestamp,
    )

    # renaming columns equaling to DB
    catalog_df.rename(
        columns={
            "Categoria": "vehicle_cat",
            "Modelo": "model",
            "Marca": "assembler",
            "Tipo de veículo": "vehicle_type",
            "Ano": "year",
            "Quilometragem": "quilometers",
            "Combustível": "gas_type",
            "Câmbio": "gearshift",
            "Portas": "doors",
            "Final de placa": "last_digit",
            "Cor": "color",
            "Direção": "steering_system",
            "Kit GNV": "gnv_kit",
            "Potência do motor": "cubic_cap",
        },
        inplace=True,
    )

    # ======================================================================================================================
    # Storing data on AWS DB
    # ======================================================================================================================
    upload_aws(host_, user_, pass_, table_, catalog_df)

    # ======================================================================================================================
    # Validation Support
    # ======================================================================================================================
    conn = pymysql.connect(host=host_, user=user_, password=pass_, db=table_)
    #cursor = conn.cursor()
    #sql = "SELECT * FROM car_ads"
    #cursor.execute(sql)
    #cursor.fetchall()
    sql_dataframe = pd.read_sql("SELECT * FROM car_ads", conn)["timestamp"]
    biggest_ts = sql_dataframe.max()
    # Get when was the last update
    print("Biggest timestamp", datetime.fromtimestamp(biggest_ts))
    # Get the total amount of registers
    print("Records number", len(sql_dataframe))
    conn.close()
