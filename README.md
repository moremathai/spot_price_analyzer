# Spot Price Analyzer

## Description
This was an experiment to use ChatGPT to generate code to track the price of
spot instances.

### Application Goal
Simple tool to track the price of spot instances. Running the tool will store a
snapshot of the price histories for the instances described into a sqlite
database. The tool will also print out the cheapest option per instance size.


## ChatGPT prompts
- Can you write a program which can get the latest aws spot instance prices for
  a list of instance types?
- Can you add error handling?
- Can you add the availability zone to the formatted print statement?
- I want to build an application that then stores the spot instance information
  into a sqlite database. Then you can query based on the price movement for a
  specific availability zone. Can you help me?
- Can you refactor the code into classes for resusability?
- Can you refactor all the interactions with sqlite to another class?
- Can you add dependency injection by allowing the caller to pass into the
  classes the SQLiteManager?

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
