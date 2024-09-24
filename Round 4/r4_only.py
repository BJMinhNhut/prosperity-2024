#
from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, UserId
import numpy as np
import pandas as pd
import math

# storing string as const to avoid typos
SUBMISSION = "SUBMISSION"
AMETHYSTS = "AMETHYSTS"
STARFRUIT = "STARFRUIT"
ORCHIDS = "ORCHIDS"
CHOCOLATE = "CHOCOLATE"
STRAWBERRIES = "STRAWBERRIES"
ROSES = "ROSES"
GIFT_BASKET = "GIFT_BASKET"
COCONUT = "COCONUT"
COCONUT_COUPON = "COCONUT_COUPON"

PRODUCTS = [
    AMETHYSTS,
    STARFRUIT,
    ORCHIDS,
    CHOCOLATE,
    STRAWBERRIES,
    ROSES,
    GIFT_BASKET,
    COCONUT,
    COCONUT_COUPON
]

DEFAULT_PRICES = {
    AMETHYSTS: 10_000,
    STARFRUIT: 5_012,
    ORCHIDS: 1_050,
    CHOCOLATE: 7_797,
    STRAWBERRIES: 4_008,
    ROSES: 14_332,
    GIFT_BASKET: 70_097,
    COCONUT: 10040,
    COCONUT_COUPON: 620,
}

POSITION_LIMIT = {
    AMETHYSTS: 20,
    STARFRUIT: 20,
    ORCHIDS: 100,
    CHOCOLATE: 250,
    STRAWBERRIES: 350,
    ROSES: 60,
    GIFT_BASKET: 60,
    COCONUT: 300,
    COCONUT_COUPON: 600
}


class Trader:

    def __init__(self) -> None:

        print("Initializing Trader...")

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

        self.prices: Dict[str, pd.Series] = {
            "GIFT_SPREAD": pd.Series(),
            "COCONUT_SPREAD": pd.Series(),
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

    def update_spread(self, state: TradingState):
        price_choco = self.get_mid_price(CHOCOLATE, state)
        price_roses = self.get_mid_price(ROSES, state)
        price_straw = self.get_mid_price(STRAWBERRIES, state)
        price_gift = self.get_mid_price(GIFT_BASKET, state)

        spread = price_gift - (price_choco*4 + price_straw*6 + price_roses)
        self.prices["GIFT_SPREAD"] = pd.concat([
            self.prices["GIFT_SPREAD"],
            pd.Series({state.timestamp: spread})
        ])

        coco_spread = self.get_mid_price(
            COCONUT, state) - 2*self.get_mid_price(COCONUT_COUPON, state)
        self.prices["COCONUT_SPREAD"] = pd.concat([
            self.prices["COCONUT_SPREAD"],
            pd.Series({state.timestamp: coco_spread})
        ])
    # Algorithm logic

    def amethysts_strategy(self, state: TradingState):
        """
        Returns a list of orders with trades of amethysts.

        Comment: Mudar depois. Separar estrategia por produto assume que
        cada produto eh tradado independentemente
        """

        position_amethysts = self.get_position(AMETHYSTS, state)

        bid_volume = POSITION_LIMIT[AMETHYSTS] - position_amethysts
        ask_volume = - POSITION_LIMIT[AMETHYSTS] - position_amethysts

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

        bid_volume = POSITION_LIMIT[STARFRUIT] - position_starfruit
        ask_volume = - POSITION_LIMIT[STARFRUIT] - position_starfruit

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

        bid_volume = POSITION_LIMIT[ORCHIDS] - position_orchids
        ask_volume = - POSITION_LIMIT[ORCHIDS] - position_orchids

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

        if position_orchids < -40 and converse.askPrice != None:
            if int(converse.askPrice) < acceptable_bid_price:
                print("BUY", str(bid_volume) + "x", converse.askPrice)
                orders.append(
                    Order(ORCHIDS, int(converse.askPrice), bid_volume))

        if state.timestamp >= 6e5 and state.timestamp <= 8e5 and len(order_depth.sell_orders) != 0:
            best_ask, best_ask_amount = list(
                order_depth.sell_orders.items())[0]
            if int(best_ask) < acceptable_bid_price:
                print("BUY", str(-best_ask_amount) + "x", best_ask)
                orders.append(Order(ORCHIDS, best_ask, -best_ask_amount))

        if state.timestamp > 8e5 and len(order_depth.buy_orders) != 0:
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            if int(best_bid) > acceptable_ask_price:
                print("SELL", str(best_bid_amount) + "x", best_bid)
                orders.append(Order(ORCHIDS, best_bid, -best_bid_amount))
        return orders

    def gift_strategy(self, state: TradingState):
        """
        Returns a list of orders with trades of gift baskets, chocolates, roses and strawberries.

                Spread = gift - (4 * choco + 6 * strawberries + roses)
                Calculate moving avg spread of 5 timestamp
                Calculate mean and std dev of 100 timestamp
                If Z < -1.65 => long: buy gift, sell contents
                If Z > 1.65 => short: buy contents, sell gift
        """
        orders_gift: List[Order] = []
        orders_choco: List[Order] = []
        orders_roses: List[Order] = []
        orders_straws: List[Order] = []

        position_chocolate = self.get_position(CHOCOLATE, state)
        position_strawberries = self.get_position(STRAWBERRIES, state)
        position_roses = self.get_position(ROSES, state)
        position_gift = self.get_position(GIFT_BASKET, state)

        bid_volume = min((POSITION_LIMIT[CHOCOLATE] - position_chocolate) // 4, (POSITION_LIMIT[STRAWBERRIES] -
                         position_strawberries) // 6, POSITION_LIMIT[ROSES]-position_roses, POSITION_LIMIT[GIFT_BASKET] - position_gift)
        ask_volume = max(- POSITION_LIMIT[GIFT_BASKET] - position_gift, (-POSITION_LIMIT[CHOCOLATE] - position_chocolate) //
                         4, (-POSITION_LIMIT[STRAWBERRIES] - position_strawberries) // 6, (-POSITION_LIMIT[ROSES]-position_roses))

        WINDOW = 100
        avg_spread = self.prices["GIFT_SPREAD"].rolling(WINDOW).mean().iloc[-1]
        std_spread = self.prices["GIFT_SPREAD"].rolling(WINDOW).std().iloc[-1]
        spread_5 = self.prices["GIFT_SPREAD"].rolling(5).mean().iloc[-1]

        if np.isnan(avg_spread):
            return orders_gift, orders_choco, orders_roses, orders_straws

        z_score = (spread_5 - avg_spread)/std_spread
        print(f"Average spread: {avg_spread}, Spread5: {
            spread_5}, Std: {std_spread}, Z: {z_score}, Bid volume: {bid_volume}, Ask volume: {ask_volume}")

        gift_price = int(self.get_mid_price(GIFT_BASKET, state))
        choco_price = int(self.get_mid_price(CHOCOLATE, state))
        straws_price = int(self.get_mid_price(STRAWBERRIES, state))
        roses_price = int(self.get_mid_price(ROSES, state))

        if z_score < -1.65:  # long
            # buy gift
            orders_gift.append(Order(GIFT_BASKET, gift_price, bid_volume))
            # sell contents
            orders_choco.append(
                Order(CHOCOLATE, choco_price, -bid_volume * 4))
            orders_straws.append(
                Order(STRAWBERRIES, straws_price, -bid_volume * 6))
            orders_roses.append(Order(ROSES, roses_price, -bid_volume))
        elif z_score > 1.65:  # short
            # buy contents
            orders_choco.append(
                Order(CHOCOLATE, choco_price, -ask_volume * 4))
            orders_straws.append(
                Order(STRAWBERRIES, straws_price, -ask_volume * 6))
            orders_roses.append(Order(ROSES, roses_price, -ask_volume))
            # sell gift
            orders_gift.append(Order(GIFT_BASKET, gift_price, ask_volume))

        return orders_gift, orders_choco, orders_roses, orders_straws

    def coconut_strategy(self, state: TradingState):
        """
        Returns a list of orders with trades of coconut.

        spread = coco - 2*coupon
        if z_score > 1.65 => long: sell coco, buy coupon
        if z_score < -1.65 => short: sell coupon, buy coco
        """

        position_coconut = self.get_position(COCONUT, state)
        position_coupon = self.get_position(COCONUT_COUPON, state)

        bid_volume = min(POSITION_LIMIT[COCONUT] - position_coconut,
                         (POSITION_LIMIT[COCONUT_COUPON] - position_coupon) // 2)
        ask_volume = max(- POSITION_LIMIT[COCONUT] - position_coconut,
                         (- POSITION_LIMIT[COCONUT_COUPON] - position_coupon) // 2)

        coconut_orders = []
        coupon_orders = []

        WINDOW = 80
        avg_spread = self.prices["COCONUT_SPREAD"].rolling(
            WINDOW).mean().iloc[-1]
        std_spread = self.prices["COCONUT_SPREAD"].rolling(
            WINDOW).std().iloc[-1]
        spread_4 = self.prices["COCONUT_SPREAD"].rolling(4).mean().iloc[-1]

        if np.isnan(avg_spread):
            return coconut_orders, coupon_orders

        z_score = (spread_4 - avg_spread)/std_spread
        print(f"Average spread: {avg_spread}, Spread4: {
            spread_4}, Std: {std_spread}, Z: {z_score}, Bid volume: {bid_volume}, Ask volume: {ask_volume}")

        coco_price = int(self.get_mid_price(COCONUT, state))
        coupon_price = int(self.get_mid_price(COCONUT_COUPON, state))

        if z_score < -1.5:  # long
            # buy coco
            coconut_orders.append(Order(COCONUT, coco_price, bid_volume))
            # sell coupon
            coupon_orders.append(
                Order(COCONUT_COUPON, coupon_price, 2*ask_volume))
        elif z_score > 1.5:  # short
            # buy coupon
            coupon_orders.append(
                Order(COCONUT_COUPON, coupon_price, 2*bid_volume))
            # sell choco
            coconut_orders.append(Order(COCONUT, coco_price, ask_volume))

        return coconut_orders, coupon_orders

    def run(self, state: TradingState):
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        self.round += 1
        pnl = self.update_pnl(state)
        self.update_ema_prices(state)
        self.update_spread(state)

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

        # GIFT_BASKET STRATEGY
        try:
            result[GIFT_BASKET], result[CHOCOLATE], result[ROSES], result[STRAWBERRIES] = self.gift_strategy(
                state)
        except Exception as e:
            print("Error in gift strategy")
            print(e)

        print("+---------------------------------+")

        # COCONUT STRATEGY
        try:
            result[COCONUT], result[COCONUT_COUPON] = self.coconut_strategy(
                state)
        except Exception as e:
            print("Error in coconut strategy")
            print(e)

        print("+---------------------------------+")

        # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE"
        conversions = 1
        return result, conversions, traderData
