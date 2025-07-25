import numpy as np
from collections import deque
from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def __init__(self, window_size=100):
        self.window_size = window_size
        self.mid_prices = deque(maxlen=window_size)
        self.z_history = deque(maxlen=30) 
        self.max_position = 60

    def calculate_z_score(self, price):
        self.mid_prices.append(price)
        if len(self.mid_prices) < self.window_size:
            return 0
        mean = np.mean(self.mid_prices)
        std = np.std(self.mid_prices)
        return (price - mean) / std if std != 0 else 0

    def detect_regime(self):
        if len(self.z_history) < self.z_history.maxlen:
            return "neutral"
        avg_z = np.mean(np.abs(self.z_history))
        if avg_z > 2:
            return "momentum"
        elif avg_z < 1.5:
            return "mean_reversion"
        return "neutral"

    def run(self, state):
        result = {}
        orders: List[Order] = []
        order_depth: OrderBook = state.order_depth["PRODUCT"]

        if not order_depth.buy_orders or not order_depth.sell_orders:
            return {}, self.max_position

        best_ask = min(order_depth.sell_orders)
        best_bid = max(order_depth.buy_orders)
        best_ask_vol = order_depth.sell_orders[best_ask]
        best_bid_vol = order_depth.buy_orders[best_bid]

        mid_price = (best_ask + best_bid) // 2
        z = self.calculate_z_score(mid_price)
        self.z_history.append(z)

        regime = self.detect_regime()

        if regime == "mean_reversion":
            if z > 2:
                orders.append(Order("PRODUCT", best_bid, -10))
            elif z < -2:
                orders.append(Order("PRODUCT", best_ask, 10))

        elif regime == "momentum":
            if z > 2:
                orders.append(Order("PRODUCT", best_ask, 10))
            elif z < -2:
                orders.append(Order("PRODUCT", best_bid, -10))

        result["PRODUCT"] = orders
        return result, self.max_position
