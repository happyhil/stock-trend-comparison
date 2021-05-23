import sys
import numpy as np
from datetime import datetime
from src.connect import DataLoad
from src import common


class StockTrendComparison:
    """Class used to load and hold stock data, and to run a trend comparison over time"""

    def __init__(self,
                 apikey,
                 config,
                 base_symbol=None,
                 comp_symbol=None,
                 symbol_list=None):
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
        """

        self.apikey = apikey
        self.config = config
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
        self.daterange = common.n_weeks_to_daterange(config['n_historical_weeks'])
        self.verbose = config['verbose']

    def run_comparison(self):
        """Run trend comparison on loaded data"""

        loader = DataLoad(self.apikey, self.config)
        data = loader.get_dailies(self.symbols, self.daterange)

        if self.verbose >= 1:
            print('=> Running analysis')

        combinations = self._unique_combinations(data.keys())
        daydata = self._orient_to_date(data)

        self.result = {}
        for c in combinations:

            if self.verbose >= 2:
                print(f'==> Comparing {c[0]} to {c[1]}')

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

        if self.verbose >= 1:
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

    def _orient_to_date(self, data, datekey='date', dformat='%Y-%m-%dT%H:%M:%S+%f'):
        """
        Convert orientation of loaded data to dates

        Parameters
        ----------
        data : dict
            Raw retrieved data dictionary from Marketstack API
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
        for k, v in data.items():
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
