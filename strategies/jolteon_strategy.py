import numpy as np
from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.history = []
        self.max_position = 350

    def calculate_z_score(self, current_price: float) -> float:
        if len(self.history) < self.window_size:
            self.history.append(current_price)
            return 0
        mean = np.mean(self.history)
        std_dev = np.std(self.history)
        z_score = (current_price - mean) / std_dev if std_dev != 0 else 0
        self.history.append(current_price)
        if len(self.history) > self.window_size:
            self.history.pop(0)
        return z_score

    def run(self, state):
        result = {}
        orders: List[Order] = []

        order_depth: OrderBook = state.order_depth['PRODUCT']

        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None

        best_ask_amount = order_depth.sell_orders[best_ask]
        best_bid_amount = order_depth.buy_orders[best_bid]

        if best_ask is not None and best_bid is not None:
            mid_price = (best_ask + best_bid) // 2
            z_score = self.calculate_z_score(mid_price)

            if z_score < -2:
                orders.append(Order("PRODUCT", best_ask, 10))
            if z_score > 2:
                orders.append(Order("PRODUCT", best_bid, -10))

        result["PRODUCT"] = orders
        return result, self.max_position
