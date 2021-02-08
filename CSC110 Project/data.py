"""CSC110 Fall 2020: Final Project (data.py)

You will need to install the requests and beautifulsoup4 packages:
    pip install requests beautifulsoup4

In PyCharm, go to File -> Settings -> Setting for the main folder (e.g. Project: data.py)
Python Interpreter -> Click on '+' symbol -> search "beautifulsoup4" -> Install Package

Mark the "Project" folder as source root.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Tuple, List
import csv
import json

import multiprocessing as mp

import time

# Both of these global variables represent the link to the USA Donation Dataset
BASE = "https://www.opensecrets.org/industries/recips.php"
URL = "?ind=E01&recipdetail=A&sortorder=U&mem=Y&cycle="


def get_donation_data_usa(year: int) -> Tuple[int, int]:
    """Returns the dict value
    representing (Year, Donation amount).

    Available datasets:
        - Donations between 1990 to 2020, every second year
        - Emissions between 2008 to 2018

    To avoid accessing the wrong value:

    Preconditions:
        - year in {2008, 2010, 2012, 2014, 2016, 2018}
    """

    raw_html = requests.get(BASE + URL + str(year)).text
    data = BeautifulSoup(raw_html, features='html.parser')

    table = data.find_all("table")[0]

    rows = table.find_all("tr")[1:]

    processed = []
    for r in rows:
        x = [a.text for a in list(r.children)]
        x[3] = int(x[3].replace("$", "").replace(",", ""))
        processed.append(x)

    total = sum(x[3] for x in processed)

    # print("Total of ${} donated to politicians in {}".format(total, year))

    return (year, total)


# example filepath: 'json/dataset_ghg_usa.json'
def read_ghg_data_usa(filepath: str, year: int) -> Tuple[int, int]:
    """Return a tuple representing the given year as the first element
    and the processed value (total amount of emission in USA) as the second element

    The processed value will contain the total ghg emission, if available;
    otherwise, it will contain the CO2 emission. It will also be rounded down.

    Preconditions:
        - 2008 <= year <= 2018
    """
    with open(filepath) as json_file:
        data = json.load(json_file)

        # The code below is possible because we know that there is only one key
        # to the corresponding json file: 'United States'

        list_of_dataset = data['United States']['data']

        processed_value = 0

        for each_data in list_of_dataset:
            if each_data['year'] == year:
                if 'total_ghg' in each_data:
                    processed_value = each_data['total_ghg']
                elif 'co2' in each_data:
                    processed_value = each_data['co2']
                break

    return (year, int(processed_value))


# 5 possible filepaths:
# 'csv/donations_1993_to_2003.csv'
# 'csv/donations_2004_to_2009.csv'
# 'csv/donations_2010_to_2012.csv'
# 'csv/donations_2013_to_2015.csv'
# 'csv/donations_2016_to_2018.csv'
def read_donation_data_canada(filepath: str) -> Dict[int, float]:
    """Return a dict with {Year: Amount of donation}.

    Due to the unavailability of the datasets specifically focused on the
    donations from oil and gas companies, we will be filtering out all other
    corporations other than the main 10 oil and gas companies in Canada.

    10 main Oil companies:
        - Suncor
        - Canadian Natural Resources
        - Imperial Oil
        - Enbridge
        - Transcanada Corps.
        - Husky Energy
        - Cenovus Energy
        - Encana
        - Talisman Energy
        - Crescent Point Energy

    Notes: "Canadian Natural Resources" has to be filtered differently
    due to the typos in the csv file.

    Available datasets:
        - Donations between 1993 to 2018, annual report
        - CO2 Emissions between 1990 to 2017

    """
    processed_totals = {}

    with open(filepath, encoding='ansi') as file:
        reader = csv.reader(file)
        # Skip header row
        next(reader)

        # note that some words have been omitted to increase accuracy of filtering
        # and to avoid filtering wrong companies
        main_oil_companies = ('Suncor', 'Canadian Natural', 'Imperial Oil',
                              'Enbridge', 'Transcanada', 'Husky', 'Cenovus',
                              'Encana', 'Talisman', 'Crescent Point')

        for row in reader:
            if row[3] == 'Corporations' and \
                    row[0] != 'N/A' and \
                    (row[4].startswith(main_oil_companies) or "Fuel" in row[4]):
                try:
                    processed_totals[int(row[0])] += float(row[-1])
                except KeyError:
                    processed_totals[int(row[0])] = float(row[-1])

    return processed_totals


def read_ghg_data_canada(year: int) -> Tuple[int, int]:
    """Return a tuple representing the given year as the first element
    and the processed value (total amount of emission OR donation, depending
    on the filepath it is being called with) as the second element.

    The second element of the returned tuple will be rounded down.

    Available datasets:
        - Donations between 1993 to 2018, annual report
        - CO2 Emissions between 1990 to 2017

    Preconditions:
        - 1993 <= year <= 2017
    """
    with open('csv/ghg_emissions_national_en.csv', encoding='ansi') as file:
        reader = csv.reader(file)
        # Skip header row
        next(reader)

        processed_total = 0

        # row is a list of strings
        for row in reader:
            if int(row[0]) == year:
                processed_total += float(row[-1])

    return (year, int(processed_total))


class UsaData:
    """A class representing data from USA.

    Instance variables:
        - data: a dictionary mapping from the year value to another dictionary
        containing the amount of donations received and the amount of
        emissions in each year, in USA
    """
    data: Dict[int, Dict[str, int]]

    def __init__(self) -> None:
        """Initializes the instance variable data."""
        self.data = {}
        for year in range(2008, 2020, 2):
            temp_dict = {'Donation': 0, 'Emission': 0}
            donation_amount = get_donation_data_usa(year)[1]
            ghg_amount = read_ghg_data_usa('json/dataset_ghg_usa.json', year)[1]
            temp_dict['Donation'] = donation_amount
            temp_dict['Emission'] = ghg_amount
            self.data[year] = temp_dict

    def get_donation(self) -> List[int]:
        """Returns a list containing donation data from USA."""
        donation_list = []
        for year in self.data:
            donation_list.append(self.data[year]['Donation'])

        return donation_list

    def get_emission(self) -> List[int]:
        """Returns a list containing emission data from USA."""
        emission_list = []
        for year in self.data:
            emission_list.append(self.data[year]['Emission'])

        return emission_list

    def get_year(self) -> List[int]:
        """Returns a list containing years from USA datasets."""
        return [year for year in self.data]


def multi_read_donation(f: str, q: mp.Queue) -> None:
    """Worker process that reads canada donation data"""
    q.put(read_donation_data_canada(f))


class CanadaData:
    """A class representing data from Canada.

    Instance variables:
        - data: a dictionary mapping from the year value to another dictionary
        containing the amount of donations received and the amount of
        emissions in each year, in Canada

    Note: it may take a few seconds to process data
    and initialize the instance variable data, since
    the given 5 donation datasets are quite large.
    """
    data: Dict[int, Dict[str, int]]

    def __init__(self) -> None:
        """Initializes the instance variable data."""
        self.data = {}

        filepaths = ['csv/donations_1993_to_2003.csv',
                     'csv/donations_2004_to_2009.csv',
                     'csv/donations_2010_to_2012.csv',
                     'csv/donations_2013_to_2015.csv',
                     'csv/donations_2016_to_2018.csv']

        q = mp.Queue()
        processes = set()
        
        for f in filepaths:
            p = mp.Process(target=multi_read_donation,
                           args=(f,q))
            p.start()
            processes.add(p)

        for p in processes:
            p.join()

        while not q.empty():
            temp_dict = q.get()
            for year in temp_dict:
                ghg_amount = read_ghg_data_canada(year)[1]
                self.data[year] = {'Donation': int(temp_dict[year]),
                                   'Emission': ghg_amount}

    def get_donation(self) -> List[int]:
        """Returns a list containing donation data from Canada."""
        donation_list = []
        for year in self.data:
            donation_list.append(self.data[year]['Donation'])

        return donation_list

    def get_emission(self) -> List[int]:
        """Returns a list containing emission data from Canada."""
        emission_list = []
        for year in self.data:
            emission_list.append(self.data[year]['Emission'])

        return emission_list

    def get_year(self) -> List[int]:
        """Returns a list containing years from USA datasets."""
        return [year for year in self.data]


if __name__ == "__main__":
    start = time.perf_counter()
    usa_data = UsaData()
    canada_data = CanadaData()
    print('Time taken', time.perf_counter() - start)
    print()
    print('Data from USA: ', usa_data.data)
    print('Data from Canada: ', canada_data.data)

    # It might take a while to run, but at the end
    # two processed datasets will be printed out; one from USA
    # and one from Canada.
