# Spot Price Analyzer

## Description
Simple tool to track the price of spot instances. Running the tool will store a snapshot of the price histories for the instances described into a sqlite database. The tool will also print out the cheapest option per instance size.

## Tool Usage
```bash
$ poetry run python src/spot_checker.py
m5zn.3xlarge is the cheapest instance type in the 3xlarge category at $0.4473
m5zn.6xlarge is the cheapest instance type in the 6xlarge category at $0.894
m5zn.12xlarge is the cheapest instance type in the 12xlarge category at $1.7808
```

## Start Sqlite3
```bash
$ sqlite3 spot_prices.db
sqlite>
```
