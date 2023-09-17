from datetime import datetime, timedelta


def n_weeks_to_daterange(n_weeks):
    """
    Set start and end date based on x historical days stated in config.yaml
    Method finds valid first and last trading days (mon-fri)

    Parameters
    ----------
    n_weeks : int
        Number of historical weeks

    Returns
    -------
    dict
        A dictionary consisting of the datefrom and dateto based on n_weeks
    """

    today = datetime.now().date()
    days_from_l_tradingday = max(1, (today.weekday() + 6) % 7 - 3)
    dateto = today - timedelta(days=days_from_l_tradingday)
    datefrom = dateto - timedelta(days=7 * n_weeks - 1)

    return {
        'datefrom': datefrom.strftime('%Y-%m-%d'),
        'dateto': dateto.strftime('%Y-%m-%d'),
    }
