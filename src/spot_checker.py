from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

import boto3
import matplotlib.pyplot as plt
import sqlite3


@dataclass
class SpotPrice:
    instance_type: str
    availability_zone: str
    price: Decimal
    timestamp: datetime


class SpotPricesManager:
    def __init__(self, db_file: str):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

        # Create table if not exists
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS spot_prices (
                instance_type TEXT,
                availability_zone TEXT,
                timestamp DATETIME,
                price NUMERIC,
                PRIMARY KEY (instance_type, availability_zone, timestamp)
            )
        """
        )
        self.conn.commit()

    def insert_spot_price(self, spot_price: SpotPrice):
        """
        Insert a new spot price into the database.
        """
        self.cursor.execute(
            """
            INSERT INTO spot_prices (instance_type, availability_zone, price, timestamp)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(instance_type, availability_zone, timestamp) DO UPDATE SET price=excluded.price;
        """,
            (
                spot_price.instance_type,
                spot_price.availability_zone,
                spot_price.price,
                spot_price.timestamp.replace(minute=0, second=0, microsecond=0),
            ),
        )
        self.conn.commit()

    def get_spot_prices(
        self,
        instance_type: str,
        availability_zone: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[SpotPrice]:
        """
        Get spot prices from the database for a given instance type.
        If an availability zone is provided, only returns prices for that zone.
        """
        if availability_zone:
            query = """
                SELECT instance_type, availability_zone, price, timestamp
                FROM spot_prices
                WHERE instance_type = ? AND availability_zone = ?
                ORDER BY timestamp DESC
            """
            params = (instance_type, availability_zone)
        else:
            query = """
                SELECT instance_type, availability_zone, price, timestamp
                FROM spot_prices
                WHERE instance_type = ?
                ORDER BY timestamp DESC
            """
            params = (instance_type,)

        if limit is not None:
            query += f" LIMIT {limit}"
        self.cursor.execute(query, params)

        rows = self.cursor.fetchall()
        return [SpotPrice(*row) for row in rows]

    def __del__(self):
        """
        Closes the database connection.
        """
        self.conn.close()


class SpotPriceFetcher:
    def __init__(self, instance_types, spot_manager):
        self.instance_types = instance_types
        self.ec2 = boto3.client("ec2")
        self.spot_manager = spot_manager

    def fetch_and_store_spot_prices(self):
        try:
            response = self.ec2.describe_spot_price_history(
                InstanceTypes=self.instance_types, ProductDescriptions=["Linux/UNIX"]
            )

            for spot_price in response["SpotPriceHistory"]:
                data = SpotPrice(
                    spot_price["InstanceType"],
                    spot_price["AvailabilityZone"],
                    spot_price["SpotPrice"],
                    spot_price["Timestamp"],
                )
                self.spot_manager.insert_spot_price(data)

        except Exception as e:
            print(f"An error occurred: {e}")


class SpotPriceGrapher:
    def __init__(self, instance_types, spot_manager):
        self.instance_types = instance_types
        self.spot_manager = spot_manager

    def plot_spot_prices_over_time(
        self, instance_type: str, availability_zone: str
    ) -> None:
        # Retrieve spot prices for the instance type
        spot_prices = self.spot_manager.get_spot_prices(
            instance_type, availability_zone
        )
        if not spot_prices:
            print(f"No spot prices found for instance type {instance_type}.")
            return

        # plot the spot_prices data
        plt.figure(figsize=(10, 5))
        plt.title(f"Spot Prices for {instance_type} in {availability_zone}")
        plt.xlabel("Time")
        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Price")
        plt.plot(
            [spot_price.timestamp for spot_price in spot_prices],
            [spot_price.price for spot_price in spot_prices],
        )
        plt.show()

    def __del__(self):
        self.spot_manager.__del__()


# Example usage
if __name__ == "__main__":
    # split the instance types into the family name and types
    instance_families = ["m5zn", "z1d"]
    instance_sizes = ["3xlarge", "6xlarge", "12xlarge"]

    # create a list of all the instance types
    all_instance_types = [
        f"{family}.{instance_size}"
        for family in instance_families
        for instance_size in instance_sizes
    ]

    spot_manager = SpotPricesManager("spot_prices.db")
    spot_price_fetcher = SpotPriceFetcher(all_instance_types, spot_manager=spot_manager)
    spot_price_fetcher.fetch_and_store_spot_prices()

    comparison_map = {
        i_size: [f"{family}.{i_size}" for family in instance_families]
        for i_size in instance_sizes
    }
    for i_size in comparison_map:
        instance_types = comparison_map[i_size]
        # find the cheapest instance type
        min_price = float("inf")
        optimal_type = ""
        for i_type in instance_types:
            price = spot_manager.get_spot_prices(
                i_type, availability_zone="us-east-1d", limit=1
            )[0].price
            if price < min_price:
                min_price = price
                optimal_type = i_type
        print(
            f"{optimal_type} is the cheapest instance type in the {i_size} category at ${min_price}"
        )
