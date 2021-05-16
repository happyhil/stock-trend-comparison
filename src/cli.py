#!/usr/bin/env python


import sys
import yaml
from src.tools import StockTrendComparison


def main():
    """"""

    with open('config.yaml', 'r') as s:
        conf = yaml.load(s, yaml.SafeLoader)
    with open('secret.yaml', 'r') as s:
        sec = yaml.load(s, yaml.SafeLoader)

    if len(sys.argv) > 1:

        if len(sys.argv) == 3:
            base = sys.argv[1]
            comp = sys.argv[2]
            comparator = StockTrendComparison(sec['apikey'],
                                              conf,
                                              base_symbol=base,
                                              comp_symbol=comp)

        elif len(sys.argv) == 2:
            comparator = StockTrendComparison(sec['apikey'],
                                              conf,
                                              symbol_list=sys.argv[1])

        comparator.load_data()
        comparator.run_comparison()
        comparator.print_results()

    else:
        for b in conf['symbols'].keys():
            comparator = StockTrendComparison(sec['apikey'],
                                              conf,
                                              symbol_list=b)
            comparator.load_data()
            comparator.run_comparison()
            comparator.print_results()


if __name__ == '__main__':
    main()
