import numpy as np
from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.history = []
        self.max_position = 100

    def calculate_z_score(self, current_price: float) -> float:
        if len(self.history) < self.window_size:
            self.history.append(current_price)
            return 0
        mean = np.mean(self.history)
        std_dev = np.std(self.history)
        z_score = (current_price - mean) / std_dev
        self.history.append(current_price)
        if len(self.history) > self.window_size:
            self.history.pop(0)
        return z_score

    def run(self, state):
        result = {}
        orders: List[Order] = []
        print(state.order_depth)
        order_depth: OrderBook = state.order_depth['PRODUCT']

        if len(order_depth.sell_orders) != 0 and len(order_depth.buy_orders) != 0:
            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]

            best_ask_price = int(best_ask)
            best_bid_price = int(best_bid)

            ask_z_score = self.calculate_z_score(best_ask_price)
            bid_z_score = self.calculate_z_score(best_bid_price)

            if ask_z_score < -2:
                orders.append(Order("PRODUCT", best_ask, -best_ask_amount))

            if bid_z_score > 2:
                orders.append(Order("PRODUCT", best_bid, -best_bid_amount))

        result["PRODUCT"] = orders
        return result, self.max_position
