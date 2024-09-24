from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

import math

# storing string as const to avoid typos
SUBMISSION = "SUBMISSION"
AMETHYSTS = "AMETHYSTS"
STARFRUIT = "STARFRUIT"

PRODUCTS = [
    AMETHYSTS,
    STARFRUIT,
]

DEFAULT_PRICES = {
    AMETHYSTS: 10_000,
    STARFRUIT: 5_000,
}


class Trader:

    def __init__(self) -> None:

        print("Initializing Trader...")

        self.position_limit = {
            AMETHYSTS: 20,
            STARFRUIT: 20,
        }

        self.round = 0

        # Values to compute pnl
        self.cash = 0
        # positions can be obtained from state.position

        # self.past_prices keeps the list of all past prices
        self.past_prices = dict()
        for product in PRODUCTS:
            self.past_prices[product] = None

        # self.ema_prices keeps an exponential moving average of prices
        self.ema_prices = dict()
        for product in PRODUCTS:
            self.ema_prices[product] = None

        self.ema_param = 0.075
        self.price_trend = {
            AMETHYSTS: 0,
            STARFRUIT: 0,
        }

    # utils

    def get_position(self, product, state: TradingState):
        return state.position.get(product, 0)

    def get_mid_price(self, product, state: TradingState):

        default_price = self.ema_prices[product]
        if default_price is None:
            default_price = DEFAULT_PRICES[product]

        if product not in state.order_depths:
            return default_price

        market_bids = state.order_depths[product].buy_orders
        if len(market_bids) == 0:
            # There are no bid orders in the market (midprice undefined)
            return default_price

        market_asks = state.order_depths[product].sell_orders
        if len(market_asks) == 0:
            # There are no bid orders in the market (mid_price undefined)
            return default_price

        best_bid = max(market_bids)
        best_ask = min(market_asks)
        return (best_bid + best_ask)/2

    def get_value_on_product(self, product, state: TradingState):
        """
        Returns the amount of MONEY currently held on the product.
        """
        return self.get_position(product, state) * self.get_mid_price(product, state)

    def update_pnl(self, state: TradingState):
        """
        Updates the pnl.
        """
        def update_cash():
            # Update cash
            for product in state.own_trades:
                for trade in state.own_trades[product]:
                    if trade.timestamp != state.timestamp - 100:
                        # Trade was already analyzed
                        continue

                    if trade.buyer == SUBMISSION:
                        self.cash -= trade.quantity * trade.price
                    if trade.seller == SUBMISSION:
                        self.cash += trade.quantity * trade.price

        def get_value_on_positions():
            value = 0
            for product in state.position:
                value += self.get_value_on_product(product, state)
            return value

        # Update cash
        update_cash()
        return self.cash + get_value_on_positions()

    def update_ema_prices(self, state: TradingState):
        """
        Update the exponential moving average of the prices of each product.
        """
        for product in PRODUCTS:
            mid_price = self.get_mid_price(product, state)
            if mid_price is None:
                continue

            # Update ema price
            if self.ema_prices[product] is None:
                self.ema_prices[product] = mid_price
                self.past_prices[product] = mid_price
            else:
                self.past_prices[product] = self.ema_prices[product]
                self.ema_prices[product] = self.ema_param * mid_price + \
                    (1-self.ema_param) * self.ema_prices[product]
                delta = self.ema_prices[product] - self.past_prices[product]
                if delta > 0:
                    self.price_trend[product] = 1
                elif delta < 0:
                    self.price_trend[product] = -1
                else:
                    self.price_trend[product] = 0

    # Algorithm logic

    def amethysts_strategy(self, state: TradingState):
        """
        Returns a list of orders with trades of amethysts.

        Comment: Mudar depois. Separar estrategia por produto assume que
        cada produto eh tradado independentemente
        """

        position_amethysts = self.get_position(AMETHYSTS, state)

        bid_volume = self.position_limit[AMETHYSTS] - position_amethysts
        ask_volume = - self.position_limit[AMETHYSTS] - position_amethysts

        orders = []
        orders.append(
            Order(AMETHYSTS, DEFAULT_PRICES[AMETHYSTS] - 2, bid_volume))
        orders.append(
            Order(AMETHYSTS, DEFAULT_PRICES[AMETHYSTS] + 2, ask_volume))

        return orders

    def starfruit_strategy(self, state: TradingState):
        """
        Returns a list of orders with trades of starfruit.

        Comment: Mudar depois. Separar estrategia por produto assume que
        cada produto eh tradado independentemente
        """

        position_starfruit = self.get_position(STARFRUIT, state)

        bid_volume = self.position_limit[STARFRUIT] - position_starfruit
        ask_volume = - self.position_limit[STARFRUIT] - position_starfruit

        orders = []

        order_depth: OrderDepth = state.order_depths[STARFRUIT]
        orders: List[Order] = []
        acceptable_bid_price = self.ema_prices[STARFRUIT]
        acceptable_ask_price = self.ema_prices[STARFRUIT]
        trend = self.price_trend[STARFRUIT]

        print("Acceptable price : " + str(self.ema_prices[STARFRUIT]))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) +
              ", Sell order depth : " + str(len(order_depth.sell_orders)))

        if trend > 0:
            acceptable_bid_price += 1
        if trend < 0:
            acceptable_ask_price -= 1

        if position_starfruit > 0:
            acceptable_bid_price -= 1
        if position_starfruit < 0:
            acceptable_ask_price += 1

        if len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(
                order_depth.sell_orders.items())[0]
            if int(best_ask) < acceptable_bid_price:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                orders.append(Order(STARFRUIT, best_ask,
                              min(bid_volume, -best_ask_amount)))

        if len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(
                order_depth.buy_orders.items())[0]
            if int(best_bid) > acceptable_ask_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                orders.append(Order(STARFRUIT, best_bid,
                              max(ask_volume, -best_bid_amount)))

        return orders

    def run(self, state: TradingState):
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """

        self.round += 1
        pnl = self.update_pnl(state)
        self.update_ema_prices(state)

        print(f"Log round {self.round}")

        print("TRADES:")
        for product in state.own_trades:
            for trade in state.own_trades[product]:
                if trade.timestamp == state.timestamp - 100:
                    print(trade)

        print(f"\tCash {self.cash}")
        for product in PRODUCTS:
            print(f"\tProduct {product}, Position {self.get_position(product, state)}, Midprice {self.get_mid_price(
                product, state)}, Value {self.get_value_on_product(product, state)}, EMA {self.ema_prices[product]}")
        print(f"\tPnL {pnl}")

        # Initialize the method output dict as an empty dict
        result = {}

        # AMETHYSTS STRATEGY
        try:
            result[AMETHYSTS] = self.amethysts_strategy(state)
        except Exception as e:
            print("Error in amethysts strategy")
            print(e)

        # STARFRUIT STRATEGY
        try:
            result[STARFRUIT] = self.starfruit_strategy(state)
        except Exception as e:
            print("Error in starfruit strategy")
            print(e)

        print("+---------------------------------+")

        # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE"
        conversions = 1
        return result, conversions, traderData
