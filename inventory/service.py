import logging

from kontiki.delegate import ServiceDelegate
from kontiki.messaging import Messenger, rpc, rpc_error
from kontiki.registry import degraded_on


class InventoryDelegate(ServiceDelegate):
    def __init__(self):
        super().__init__()
        self.stock = {"MUG": 5, "VASE": 1}
        self.prices = {"MUG": 12}
        self.crashed = False

    async def reserve(self, sku, qty, order_id):
        logging.info("Reserving %s x %s for %s", qty, sku, order_id)
        available = self.stock.get(sku)
        if available is None:
            logging.info("Unknown sku %s for %s", sku, order_id)
            return rpc_error("UNKNOWN_SKU", f"Unknown sku {sku}")
        if available < qty:
            logging.info("Out of stock for %s: asked %s, have %s", sku, qty, available)
            return rpc_error("OUT_OF_STOCK", f"Only {available} {sku} left")
        if sku not in self.prices:
            self.crashed = True
            logging.error("No price for %s, order %s", sku, order_id)
            raise RuntimeError(f"no price for {sku}")

        self.stock[sku] = available - qty
        await self.container.messenger.publish(
            "stock.reserved",
            {"order_id": order_id, "sku": sku, "qty": qty},
        )
        logging.info("Reserved %s x %s for %s", qty, sku, order_id)
        return {"sku": sku, "qty": qty, "unit_price": self.prices[sku]}

    def is_degraded(self):
        if self.crashed:
            return True, "reserve crashed"
        return False


class Inventory:
    name = "Inventory"
    delegate = InventoryDelegate()
    messenger = Messenger()

    @rpc
    async def reserve(self, sku, qty, order_id):
        return await self.delegate.reserve(sku, qty, order_id)

    @degraded_on
    def is_degraded(self):
        return self.delegate.is_degraded()
