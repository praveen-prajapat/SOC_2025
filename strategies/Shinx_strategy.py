import numpy as np
from collections import deque
from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def __init__(self, window_size=200):
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
        if avg_z > 2.0:
            return "momentum"
        elif avg_z < 1.0:
            return "mean_reversion"
        return "neutral"

    def run(self, state):
        result = {}
        orders: List[Order] = []
        product = "PRODUCT"
        orderbook: OrderBook = state.order_depth[product]
        position = state.positions['PRODUCT']

        if not orderbook.buy_orders or not orderbook.sell_orders:
            return {}, self.max_position

        best_ask = min(orderbook.sell_orders)
        best_bid = max(orderbook.buy_orders)
        best_ask_vol = orderbook.sell_orders[best_ask]
        best_bid_vol = orderbook.buy_orders[best_bid]

        mid_price = (best_ask + best_bid) // 2
        z = self.calculate_z_score(mid_price)
        self.z_history.append(z)
        regime = self.detect_regime()

        if regime == "mean_reversion":
            if z > 2.3 and position > -self.max_position:
                orders.append(Order(product, best_bid, -5))
            elif z < -2.3 and position < self.max_position:
                orders.append(Order(product, best_ask, 5))
            elif abs(z) < 0.3 and position != 0:
                exit_size = -position
                price = best_bid if exit_size > 0 else best_ask
                orders.append(Order(product, price, exit_size))

        elif regime == "momentum":
            if z > 1.2 and position < self.max_position:
                orders.append(Order(product, best_bid, 10))
            elif z < -2.0 and position > -self.max_position:
                orders.append(Order(product, best_ask, -10))
            elif abs(z) < 0.3 and position != 0:
                exit_size = -position
                price = best_bid if exit_size > 0 else best_ask
                orders.append(Order(product, price, exit_size))

        result[product] = orders
        return result, self.max_position
