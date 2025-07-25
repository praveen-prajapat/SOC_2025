from src.backtester import Order, OrderBook
from typing import List

class Trader:
    def __init__(self):
        self.max_position = 20
        self.position = 0

    def run(self, state):
        result = {}
        orders: List[Order] = []
        order_depth: OrderBook = state.order_depth['PRODUCT']
        order_size = 3

        if order_depth.buy_orders:
            best_bid, best_bid_amount = list(sorted(order_depth.buy_orders.items(), reverse=True))[0]
        else:
            best_bid, best_bid_amount = None, 0

        if order_depth.sell_orders:
            best_ask, best_ask_amount = list(sorted(order_depth.sell_orders.items()))[0]
        else:
            best_ask, best_ask_amount = None, 0

        if best_bid is not None and self.position < self.max_position:
            buy_volume = min(order_size, self.max_position - self.position, abs(best_bid_amount))
            if buy_volume > 0:
                orders.append(Order("PRODUCT", best_bid, buy_volume))
                self.position += buy_volume

        if best_ask is not None and self.position > -self.max_position:
            sell_volume = min(order_size, self.max_position + self.position, abs(best_ask_amount))
            if sell_volume > 0:
                orders.append(Order("PRODUCT", best_ask, -sell_volume))
                self.position -= sell_volume

        result["PRODUCT"] = orders
        return result, self.max_position
