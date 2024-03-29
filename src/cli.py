#!/usr/bin/env python


import click
import yaml
from src import tools


@click.command()
@click.option('-b', '--base', default=None, help='Base stock symbol to check on.')
@click.option('-c', '--comp', default=None, help='Stock symbol to compare.')
@click.option('-s', '--syms', default=None, help='Value referring to one of the symbol lists in config.yaml.')
def relative_comparison(base, comp, syms):
    """
    Main stock comparison execution

    Parameters
    ----------
    base : str, optional
        Base stock symbol (default is None)
    comp : str, optional
        Stock symbol to compare (default is None)
    syms : str, optional
        Value referring to one of the symbol lists in config.yaml (default is None)
    """

    with open('config.yaml', 'r') as s:
        conf = yaml.load(s, yaml.SafeLoader)
    with open('secret.yaml', 'r') as s:
        sec = yaml.load(s, yaml.SafeLoader)

    if base is not None or comp is not None or syms is not None:

        if base is not None or comp is not None:
            comparator = tools.StockTrendComparison(sec['apikey'],
                                                    conf,
                                                    base_symbol=base,
                                                    comp_symbol=comp)

        if syms is not None:
            comparator = tools.StockTrendComparison(sec['apikey'],
                                                    conf,
                                                    symbol_list=syms)
        comparator.run_comparison()
        comparator.print_results()

    else:
        for b in conf['symbols'].keys():
            comparator = tools.StockTrendComparison(sec['apikey'],
                                                    conf,
                                                    symbol_list=b)
            comparator.run_comparison()
            comparator.print_results()


@click.command()
@click.option('-b', '--base', default=None, help='Base stock symbol to check on.')
def weekonweek_comparison(base):
    pass
