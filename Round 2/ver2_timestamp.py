#
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, UserId

import math

# storing string as const to avoid typos
SUBMISSION = "SUBMISSION"
AMETHYSTS = "AMETHYSTS"
STARFRUIT = "STARFRUIT"
ORCHIDS = "ORCHIDS"

PRODUCTS = [
    AMETHYSTS,
    STARFRUIT,
    ORCHIDS,
]

DEFAULT_PRICES = {
    AMETHYSTS: 10_000,
    STARFRUIT: 5_012,
    ORCHIDS: 1_050,
}


class Trader:

    def __init__(self) -> None:

        print("Initializing Trader...")

        self.position_limit = {
            AMETHYSTS: 20,
            STARFRUIT: 20,
            ORCHIDS: 100,
        }

        self.round = 0

        # Values to compute pnl
        self.cash = 0
        # positions can be obtained from state.position

        # self.past_prices keeps the list of all past prices
        self.past_prices = dict()
        for product in PRODUCTS:
            self.past_prices[product] = []

        # self.ema_prices keeps an exponential moving average of prices
        self.ema_prices = dict()
        for product in PRODUCTS:
            self.ema_prices[product] = None

        self.ema_param = 0.06625

    # utils

    def get_position(self, product, state: TradingState):
        return state.position.get(product, 0)

    def get_mid_price(self, product, state: TradingState):

        if product == ORCHIDS:
            conversion = state.observations.conversionObservations[ORCHIDS]
            ask_price = conversion.askPrice
            bid_price = conversion.bidPrice
            if ask_price == None and bid_price == None:
                return DEFAULT_PRICES[ORCHIDS]
            if ask_price == None:
                return bid_price
            if bid_price == None:
                return ask_price
            return (ask_price + bid_price)/2

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
            conversion = state.observations.conversionObservations[ORCHIDS]
            # Update cash
            for product in state.own_trades:
                for trade in state.own_trades[product]:
                    if trade.timestamp != state.timestamp - 100:
                        # Trade was already analyzed
                        continue

                    extra_cost = 0
                    if product == ORCHIDS:
                        extra_cost = conversion.transportFees + conversion.importTariff
                    if trade.buyer == SUBMISSION:
                        self.cash -= trade.quantity * \
                            (trade.price + extra_cost)
                    if trade.seller == SUBMISSION:
                        self.cash += trade.quantity * \
                            (trade.price - extra_cost)

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
            else:
                self.ema_prices[product] = self.ema_param * mid_price + \
                    (1-self.ema_param) * self.ema_prices[product]

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
        # orders.append(Order(STARFRUIT, math.floor(self.ema_prices[STARFRUIT] - 1), bid_volume))
        # orders.append(Order(STARFRUIT, math.ceil(self.ema_prices[STARFRUIT] + 2), ask_volume))
        if position_starfruit == 0:
            # Not long nor short
            orders.append(Order(STARFRUIT, math.floor(
                self.ema_prices[STARFRUIT] - 1.5), bid_volume))
            orders.append(Order(STARFRUIT, math.ceil(
                self.ema_prices[STARFRUIT] + 1.5), ask_volume))

        if position_starfruit > 0:
            # Long position
            bid_bonus = math.ceil(position_starfruit / 6.67) + 1
            orders.append(Order(STARFRUIT, math.floor(
                self.ema_prices[STARFRUIT] - bid_bonus), bid_volume))
            orders.append(Order(STARFRUIT, math.ceil(
                self.ema_prices[STARFRUIT] + 1), ask_volume))

        if position_starfruit < 0:
            # Short position
            ask_bonus = math.ceil(position_starfruit / -6.67) + 1
            orders.append(Order(STARFRUIT, math.floor(
                self.ema_prices[STARFRUIT] - 1), bid_volume))
            orders.append(Order(STARFRUIT, math.ceil(
                self.ema_prices[STARFRUIT] + ask_bonus), ask_volume))

        return orders

    def orchids_strategy(self, state: TradingState):
        """
        Returns a list of orders with trades of orchids.

                Sell: price reduced by Export Tariff + shipping cost
                Buy: price increase by Import Tariff + shipping cost
        """

        position_orchids = self.get_position(ORCHIDS, state)

        bid_volume = self.position_limit[ORCHIDS] - position_orchids
        ask_volume = - self.position_limit[ORCHIDS] - position_orchids

        order_depth: OrderDepth = state.order_depths[ORCHIDS]
        orders: List[Order] = []
        converse = state.observations.conversionObservations[ORCHIDS]

        acceptable_bid_price = self.ema_prices[ORCHIDS]
        acceptable_ask_price = self.ema_prices[ORCHIDS]

        if converse.bidPrice != None:
            if int(converse.bidPrice) > acceptable_ask_price:
                print("SELL", str(ask_volume) + "x", converse.bidPrice)
                orders.append(
                    Order(ORCHIDS, int(converse.bidPrice), ask_volume))

        if position_orchids < -20 and converse.askPrice != None:
            if int(converse.askPrice) < acceptable_bid_price:
                print("BUY", str(bid_volume) + "x", converse.askPrice)
                orders.append(
                    Order(ORCHIDS, int(converse.askPrice), bid_volume))

        if state.timestamp >= 700000 and state.timestamp <= 810000 and len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(
                order_depth.sell_orders.items())[0]
            if int(best_ask) < acceptable_bid_price:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                orders.append(Order(ORCHIDS, best_ask, -best_ask_amount))

        if state.timestamp > 810000 and len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if int(best_bid) > acceptable_ask_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                orders.append(Order(ORCHIDS, best_bid, -best_bid_amount))
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

        # ORCHIDS STRATEGY
        try:
            result[ORCHIDS] = self.orchids_strategy(state)
        except Exception as e:
            print("Error in orchids strategy")
            print(e)

        print("+---------------------------------+")

        # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE"
        conversions = 1
        return result, conversions, traderData
