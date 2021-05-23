import sys
import time
import requests
from datetime import datetime


class DataLoad:
    """Class used to load data from Marketstack API"""

    def __init__(self, apikey, config):
        """"
        Parameters
        ----------
        apikey : str
            Account API key
        config : dict
            Project configuration dictionary loaded from config.yaml
        """

        self.apikey = apikey
        self.baseurl = config['baseurl']
        self.verbose = config['verbose']

    def get_dailies(self, symbols, daterange, max_requests=5, endpoint='/v1/eod'):
        """
        Load data for initialized symbols

        Parameters
        ----------
        symbols : list
            List of symbols for which data will be loaded
        daterange : dict
            Dictionary consisting of the datefrom and dateto
        max_requests : int
            Maximum number of requests allowed within same second (default is 5)
        endpoint : str
            Endpoint to use (default is /v1/eod)

        Returns
        -------
        dict
            A dictionary with the loaded data
        """

        if self.verbose >= 1:
            print('=> Loading data')

        data = {}
        starttime, request_pressure = time.time(), 0
        for sym in symbols:

            if self.verbose >= 2:
                print(f'==> Loading {sym}')

            params = {
                'access_key': self.apikey,
                'symbols': sym,
                'date_from': daterange['datefrom'],
                'date_to': daterange['dateto'],
                'limit': abs(
                    datetime.strptime(daterange['dateto'],
                                      '%Y-%m-%d') - datetime.strptime(daterange['datefrom'],
                                                                      '%Y-%m-%d')
                ).days
            }

            targeturl = self.baseurl + endpoint
            response = requests.get(targeturl, params=params)
            response_json = response.json()
            try:
                data[sym] = response_json['data']
                retreived_ratio = round(
                    (response_json['pagination']['count'] / response_json['pagination']['total']) * 100, 1)
                if self.verbose >= 2:
                    print(f"===> Loaded {retreived_ratio}% of available objects within query")
                    print(f"===> First date: {data[sym][-1]['date']}, last date: {data[sym][1]['date']}")
            except KeyError:
                print(f'Error: no data found for {sym}, check symbol')
                if len(self.symbols) == 1:
                    sys.exit(1)

            endtime = time.time()
            request_pressure += 1
            if (endtime - starttime) >= 1:
                starttime, request_pressure = time.time(), 0
            elif request_pressure >= max_requests:
                if self.verbose >= 2:
                    print('===> sleep for 5 seconds to prevent too much requests at the same time')
                time.sleep(5)
                starttime, request_pressure = time.time(), 0
            else:
                pass

        if self.verbose >= 1:
            print('=> Loading data completed')

        return data

    def get_one_day(self, symbols, date, max_requests=5, endpoint='/v1/intraday/'):
        """
        Load data for initialized symbols

        Parameters
        ----------
        symbols : list
            List of symbols for which data will be loaded
        date : str
            Target date for data load in format %Y-%m-%d
        max_requests : int
            Maximum number of requests allowed within same second (default is 5)
        endpoint : str
            Endpoint to use (default is /v1/intraday/)

        Returns
        -------
        dict
            A dictionary with the loaded data
        """

        if self.verbose >= 1:
            print('=> Loading data')

        data = {}
        starttime, request_pressure = time.time(), 0
        for sym in symbols:

            if self.verbose >= 2:
                print(f'==> Loading {sym}')

            params = {
                'access_key': self.apikey,
                'symbols': sym,
                'interval': '15min'
            }

            targeturl = self.baseurl + endpoint + date
            response = requests.get(targeturl, params=params)
            response_json = response.json()
            try:
                data[sym] = response_json['data']
                retreived_ratio = round(
                    (response_json['pagination']['count'] / response_json['pagination']['total']) * 100, 1)
                if self.verbose >= 2:
                    print(f"===> Loaded {retreived_ratio}% of available objects within query")
                    print(f"===> First date: {data[sym][-1]['date']}, last date: {data[sym][1]['date']}")
            except KeyError:
                print(f'Error: no data found for {sym}, check symbol')
                if len(self.symbols) == 1:
                    sys.exit(1)

            endtime = time.time()
            request_pressure += 1
            if (endtime - starttime) >= 1:
                starttime, request_pressure = time.time(), 0
            elif request_pressure >= max_requests:
                if self.verbose >= 2:
                    print('===> sleep for 5 seconds to prevent too much requests at the same time')
                time.sleep(5)
                starttime, request_pressure = time.time(), 0
            else:
                pass

        if self.verbose >= 1:
            print('=> Loading data completed')

        return data
