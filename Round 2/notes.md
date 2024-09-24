Summarizing trading microstructure of ORCHIDs:
    •    ConversionObservation(https://imc-prosperity.notion.site/Writing-an-Algorithm-in-Python-658e233a26e24510bfccf0b1df647858#44efb36257b94733887ae00f46a805f1) shows quotes of ORCHID offered by the ducks from South Archipelago
    •    If you want to purchase 1 unit of ORCHID from the south, you will purchase at the askPrice, pay the TRANSPORT_FEES, IMPORT_TARIFF 
    •    If you want to sell 1 unit of ORCHID to the south, you will sell at the bidPrice, pay the TRANSPORT_FEES, EXPORT_TARIFF
    •    You can ONLY trade with the south via the conversion request with applicable conditions as mentioned in the wiki
    •    For every 1 unit of ORCHID net long position you hold, you will pay 0.1 Seashells per timestamp you hold that position. No storage cost applicable to net short position
    •    Negative ImportTariff would mean you would receive premium for importing ORCHIDs to your island
    •    Each Day in ORCHID trading is equivalent to 12 hours on the island. You can assume the ORCHID quality doesn’t deteriorate overnight
    •    Sunlight unit: Average sunlight per hour is 2500 units. The data/plot shows instantaneous rate of sunlight on any moment of the day
