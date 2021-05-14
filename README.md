# Stock Trend Comparisons

intro text here

The default settings are a year-round comparison (last 365 days) on the indicators' close value. The settings are adjustable via the `config.yaml`.

## Installation

Create a virtual environment in the root of the project. Make sure to use `python3.7` or higher.
```bash
$ virtual -p python3 venv
$ source venv/bin/activate
```

Copy the default `secret.yaml` and replace the API key.
```bash
$ cp secret.default.yaml secret.yaml
$ nano secret.yaml
```

Install the project library
```bash
$ pip install -e .
```

## Usage

To compare to indicators, use the command `run-stock-comparator <base.symb> <comp.symb>`. For example:
```bash
$ run-stock-comparator AEX.INDX HSI.INDX
```

Alternatively, use one of the symbol lists available in the `config.yaml`, which compares listed indicators.
```bash
$ run-stock-comparator indices
```

Or just run the comparator within using its parameters. The command will use then all the available symbol lists in the `config.yaml`.
```bash
$ run-stock-comparator
```
