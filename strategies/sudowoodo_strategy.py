from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def __init__(self):
        self.max_position = 10

    def run(self, state):
        result = {}
        orders: List[Order] = []
        order_depth: OrderBook = state.order_depth

        orders.append(Order("PRODUCT", 9998, 10))
        orders.append(Order("PRODUCT", 10002, -10))

        result["PRODUCT"] = orders
        return result, self.max_position
        
