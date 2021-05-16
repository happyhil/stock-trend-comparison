# Stock Trend Comparisons :chart:

Stock Trend Comparisons is a library to compare financial products on its price developments over time. The tool helps to see whether two financial products are correlated, and which of the two products might be over- or under valued.

## Installation

Preferably, create a virtual environment in the root of the project. Make sure to use `python3.7` or higher.
```bash
virtualenv -p python3 venv
source venv/bin/activate
```

Stock data are derived from [Marketstack](https://marketstack.com/)'s API. In order to connect to this environment, copy the default `secret.yaml` file and enter your API key.
```bash
cp secret.default.yaml secret.yaml
nano secret.yaml
```

Install the project library and dependencies.
```bash
pip install -e .
```

## Usage

The tool calculates the growth (as an index) between the starting- and end price for the loaded products, the absolute growth differences, and the correlation between the daily values of the loaded products over time.

To run a comparison on two financial products, use the command `run-stock-comparison -b <basesymb> -c <compsymb>`. All available products and its symbols can be looked up through the [search page](https://marketstack.com/search) of Marketstack. For example, to compare the AEX index to the HSI index, enter the following command:
```bash
run-stock-comparison -b AEX.INDX -c HSI.INDX
```

Alternatively, use one of the symbol lists stated in the `config.yaml` file, which compares all listed products to each other. For example, load all products listed under `stocks` or `indices`.
```bash
run-stock-comparison -s indices
```

Or run the comparison tool without using any paramaters at all. In this case, the tool will run a comparison on all available symbols listed in the `config.yaml` file.
```bash
run-stock-comparison
```

## Settings

By default, the following settings are applied.

- Comparison period: last 52 weeks
- Comparison on: close prices

The settings are adjustable via the `config.yaml` file.
