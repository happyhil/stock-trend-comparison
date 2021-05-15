# Stock Trend Comparisons :chart:

Stock Trend Comparisons is a library to compare two financial products on its prices over time. The tool helps to see whether two financial products are correlated, and which of the two products might be over- or under valued.

## Installation

Create a virtual environment in the root of the project. Make sure to use `python3.7` or higher.
```bash
virtual -p python3 venv
source venv/bin/activate
```

Stock data are derived from [marketstack](https://marketstack.com/)'s API. In order to connect to this environment, copy the default `secret.yaml` file and enter your API key.
```bash
cp secret.default.yaml secret.yaml
nano secret.yaml
```

Install the project library and dependencies.
```bash
pip install -e .
```

## Usage

To run a comparison on two financial products, use the command `run-stock-comparator <base.symb> <comp.symb>`. For example, to compare the AEX index to the HSI index, enter the following command:
```bash
run-stock-comparator AEX.INDX HSI.INDX
```

The tool will calculate the growth (as an index) between the starting- and end price for both products, the absolute difference between these growths, and the correlation between the prices of the two products over time.

Alternatively, use one of the symbol lists available in the `config.yaml` file, which compares all listed products to each other. For example `stocks` or `indices`.
```bash
run-stock-comparator indices
```

Or run the comparator without using paramaters at all. In this case, the tool will run on a comparison all available symbols listed in the `config.yaml` file.
```bash
run-stock-comparator
```

## Settings

By default, the following settings are applied.

- Comparison period: last 365 days
- Comparison on: close prices

The settings are adjustable via the `config.yaml`.
