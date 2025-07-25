import numpy as np
from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def __init__(self, window_size: int = 100, scale: float = 50.0):
        self.window_size = window_size
        self.scale = scale
        self.history: List[float] = []
        self.position = 0
        self.max_position = 250

    def run(self, state):
        result = {}
        orders: List[Order] = []

        order_depth: OrderBook = state.order_depth['PRODUCT']
        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None

        if best_ask is not None and best_bid is not None:
            mid_price = (best_ask + best_bid) / 2.0
            self.history.append(mid_price)

            if len(self.history) >= self.window_size:
                window = self.history[-self.window_size:]
                mean = np.mean(window)
                std_dev = np.std(window)
                std = std_dev if std_dev > 0 else 1.0
                deviation = (mid_price - mean) / std
                desired_position = int(-self.scale * deviation)
                desired_position = max(-self.max_position, min(self.max_position, desired_position))
                delta_pos = desired_position - self.position
                step = min(abs(delta_pos), 20)
                if delta_pos > 0:
                    orders.append(Order("PRODUCT", best_ask, -step))
                    self.position += step
                elif delta_pos < 0:
                    orders.append(Order("PRODUCT", best_bid, step))
                    self.position -= step

        result["PRODUCT"] = orders
        return result, self.max_position
