import sys
import time
import requests
import numpy as np
from datetime import datetime, timedelta


class StockTrendComparison:
    """Class used to load and hold stock data, and to run a trend comparison over time"""

    def __init__(self,
                 apikey,
                 config,
                 base_symbol=None,
                 comp_symbol=None,
                 symbol_list=None,
                 compare_on='close'):
        """
        Parameters
        ----------
        apikey : str
            Account API key
        config : dict
            Project configuration dictionary loaded from config.yaml
        base_symbol : str, optional
            Base symbol (default is None)
        comp_symbol : str, optional
            Compare symbol (default is None)
        symbol_list : str, optional
            Reference to symbol list in config.yaml (default is None)
        compare_on : str, optional
            Data point on which prices will be compared (default is close)
        """

        self.apikey = apikey
        self.baseurl = config['baseurl']
        self.compare_key = config['compare_on']
        self.n_weeks = config['n_historical_weeks']
        if symbol_list is not None:
            try:
                self.symbols = config['symbols'][symbol_list].values()
            except KeyError:
                print(f"Problem in symbol list:\n'{symbol_list}' not found in config,yaml, " \
                      "set symbol_list to one of the symbol lists in config.yaml, or set base_symbol " \
                      "and comp_symbol to symbols to compare")
                sys.exit(1)
        else:
            self.symbols = [base_symbol, comp_symbol]
            self.symbols = [s for s in self.symbols if s is not None]
            if len(self.symbols) == 0:
                print("Warning: no symbols set\n" \
                      "set symbol_list to one of the symbol lists in config.yaml, or set base_symbol " \
                      "and comp_symbol to symbols to compare")
        self._set_daterange()
        self.verbose = config['verbose']

    def load_data(self, max_requests=5):
        """
        Load data for initialized symbols

        Parameters
        ----------
        max_requests : int
            Maximum number of requests allowed within same second (default is 5)
        """

        if self.verbose == 1:
            print('=> Loading data')
        self.data = {}

        starttime, request_pressure = time.time(), 0
        for sym in self.symbols:

            if self.verbose == 2:
                print(f'==> Loading {sym}')

            params = {
                'access_key': self.apikey,
                'symbols': sym,
                'date_from': self.daterange['datefrom'],
                'date_to': self.daterange['dateto'],
                'limit': round(self.n_weeks * 6)
            }

            response = requests.get(self.baseurl, params=params)
            response_json = response.json()
            try:
                self.data[sym] = response_json['data']
                retreived_ratio = round(
                    (response_json['pagination']['count'] / response_json['pagination']['total']) * 100, 1)
                if self.verbose == 2:
                    print(f"==> Loaded {retreived_ratio}% of available objects within query")
            except KeyError:
                print(f'Error: no data found for {sym}, check symbol')
                if len(self.symbols) == 2:
                    sys.exit(1)

            endtime = time.time()
            request_pressure += 1
            if (endtime - starttime) >= 1:
                starttime, request_pressure = time.time(), 0
            elif request_pressure >= max_requests:
                if self.verbose == 2:
                    print('===> sleep for 5 seconds to prevent too much requests at the same time')
                time.sleep(5)
                starttime, request_pressure = time.time(), 0
            else:
                pass

        if self.verbose == 1:
            print('=> Loading data completed')

    def run_comparison(self):
        """Run trend comparison on loaded data"""

        if self.verbose == 1:
            print('=> Running analysis')

        combinations = self._unique_combinations(self.data.keys())
        daydata = self._orient_to_date()

        self.result = {}
        for c in combinations:

            if self.verbose == 2:
                print(f'==> Comparing {c}')

            dates, closes = [], []
            for k, v in daydata.items():
                if c[0] in v.keys() and c[1] in v.keys():
                    dates.append(k)
                    closes.append([v[c[0]], v[c[1]]])

            first_available_date = min([datetime.strptime(d, '%Y-%m-%d') for d in dates]).strftime('%Y-%m-%d')
            last_available_date = max([datetime.strptime(d, '%Y-%m-%d') for d in dates]).strftime('%Y-%m-%d')
            correlation_c = round(np.corrcoef([v[0] for v in closes], [v[1] for v in closes])[0][1], 3)
            self.result.update({
                f'{c[0]}-{c[1]}': {
                    'correlation_score': correlation_c,
                    'start': {
                        'date': first_available_date,
                        c[0]: daydata[first_available_date][c[0]],
                        c[1]: daydata[first_available_date][c[1]]
                    },
                    'end': {
                        'date': last_available_date,
                        c[0]: daydata[last_available_date][c[0]],
                        c[1]: daydata[last_available_date][c[1]]
                    },
                    'index': {
                        c[0]: round(daydata[last_available_date][c[0]] / daydata[first_available_date][c[0]], 3),
                        c[1]: round(daydata[last_available_date][c[1]] / daydata[first_available_date][c[1]], 3)
                    }
                }
            })

        if self.verbose == 1:
            print('=> Analysis completed')

    def print_results(self):
        """Print comparison results"""

        print('==> Comparison output:')

        for k, v in self.result.items():
            symb_base = k.split('-')[0]
            index_base = v['index'][symb_base]
            symb_comp = k.split('-')[1]
            index_comp = v['index'][symb_comp]

            index_difference = round(index_base - index_comp, 3)

            symbol_lable = f"{symb_base} (idx = {round(index_base, 2)}) x {symb_comp} (idx = {round(index_comp, 2)})"
            print(
                f"===> {symbol_lable}: growth difference = {index_difference}, correlation = {v['correlation_score']}")

    def _set_daterange(self):
        """
        Set start and end date based on x historical days stated in config.yaml
        Method finds valid first and last trading days (mon-fri)
        """

        today = datetime.now().date()
        days_from_l_tradingday = max(1, (today.weekday() + 6) % 7 - 3)
        dateto = today - timedelta(days=days_from_l_tradingday)
        datefrom = dateto - timedelta(days=7 * self.n_weeks - 1)

        self.daterange = {
            'datefrom': datefrom.strftime('%Y-%m-%d'),
            'dateto': dateto.strftime('%Y-%m-%d'),
        }

    def _orient_to_date(self, datekey='date', dformat='%Y-%m-%dT%H:%M:%S+%f'):
        """
        Convert orientation of loaded data to dates

        Parameters
        ----------
        datekey : str
            Key in which date value exists (default is date)
        dformat : str
            Format of date values (default is %Y-%m-%dT%H:%M:%S+%f)

        Returns
        -------
        dict
            A dictionary orientated on dates instead of symbols
        """

        output = {}
        for k, v in self.data.items():
            for i in v:
                date = datetime.strptime(i[datekey], dformat).strftime('%Y-%m-%d')
                if date not in output.keys():
                    output[date] = {}
                output[date].update({k: i[self.compare_key]})

        return output

    def _unique_combinations(self, values):
        """
        Generate all unique combinations for list of values

        Parameters
        ----------
        values : list
            List of symbols

        Returns
        -------
        list
            A list all unique combinations
        """

        combinations = []
        for basev in values:
            for iterv in values:
                if basev != iterv:
                    comb = sorted([basev, iterv])
                    if comb not in combinations:
                        combinations.append(comb)

        return combinations
