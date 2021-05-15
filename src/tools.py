import time
import requests
import numpy as np
from datetime import datetime, timedelta


class StockTrendComparison:
    """"""

    def __init__(self,
                 apikey,
                 config,
                 base_symbol=None,
                 comp_symbol=None,
                 symbol_list=None,
                 compare_on='close',
                 verbose=False):
        """"""

        self.apikey = apikey
        self.baseurl = config['baseurl'] # TODO: key direct
        self.compare_key = config['compare_on'] # TODO: to config.yaml
        self.n_weeks = config['n_historical_weeks']
        if symbol_list != None:
            try:
                self.symbols = config['symbols'][symbol_list].values()
            except ValueError:
                print("set sys.argv[1] to one of the symbol lists in config.yaml")
        else:
            try:
                self.symbols = [base_symbol, comp_symbol]
            except ValueError:
                print("set sys.argv[1] and sys.argv[2] to symbols")
        self._set_daterange()
        self.verbose = verbose


    def load_data(self):
        """"""

        if self.verbose:
            print('=> Loading data')
        self.data = {}

        for sym in self.symbols:

            if self.verbose:
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
            self.data[sym] = response_json['data']

            retreived_ratio = round((response_json['pagination']['count'] / response_json['pagination']['total']) * 100, 1)
            if self.verbose:
                print(f"==> Loaded {retreived_ratio}% of available objects within query")

        if self.verbose:
            print('=> Loading data completed')


    def run_comparison(self):
        """"""

        if self.verbose:
            print('=> Running analysis')

        combinations = self._unique_combinations(self.data.keys())
        daydata = self._orient_to_date()

        self.result = {}
        for c in combinations:

            if self.verbose:
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

        if self.verbose:
            print('=> Analysis completed')


    def print_results(self):

        for k, v in self.result.items():

            symb_base = k.split('-')[0]
            index_base = v['index'][symb_base]
            symb_comp = k.split('-')[1]
            index_comp = v['index'][symb_comp]

            index_difference = round(index_base - index_comp, 3)

            symbol_lable = f"{symb_base} (idx: {round(index_base, 2)}) x {symb_comp} (idx: {round(index_comp, 2)})"
            print(f"{symbol_lable} ==> growth difference: {index_difference}, correlation: {v['correlation_score']}")


    def _set_daterange(self):
        """"""

        today = datetime.now().date()
        days_from_l_tradingday = max(1, (today.weekday() + 6) % 7 - 3)
        dateto = today - timedelta(days = days_from_l_tradingday)
        datefrom = dateto - timedelta(days = 7 * self.n_weeks - 1)

        self.daterange = {
            'datefrom': datefrom.strftime('%Y-%m-%d'),
            'dateto': dateto.strftime('%Y-%m-%d'),
        }


    def _orient_to_date(self, datekey='date', dformat='%Y-%m-%dT%H:%M:%S+%f'):
        """"""

        output = {}
        for k, v in self.data.items():
            for i in v:
                date = datetime.strptime(i[datekey], dformat).strftime('%Y-%m-%d')
                if date not in output.keys():
                    output[date] = {}
                output[date].update({k: i[self.compare_key]})

        return output


    def _unique_combinations(self, values):
        """"""

        combinations = []
        for basev in values:
            for iterv in values:
                if basev != iterv:
                    comb = sorted([basev, iterv])
                    if comb not in combinations:
                        combinations.append(comb)

        return combinations
