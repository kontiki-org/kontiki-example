import logging

from kontiki.delegate import ServiceDelegate
from kontiki.messaging import (
    Messenger,
    RpcClientError,
    RpcProxy,
    RpcServerError,
    rpc,
    rpc_error,
)


class CheckoutDelegate(ServiceDelegate):
    async def place_order(self, order_id, sku, qty):
        logging.info("Placing order %s: %s x %s", order_id, qty, sku)
        inventory = RpcProxy(self.container.messenger, peer="inventory")
        try:
            reservation = await inventory.reserve(sku=sku, qty=qty, order_id=order_id)
        except RpcClientError as exc:
            logging.info("Order %s rejected: %s", order_id, exc.code)
            await self.add_context(
                {
                    "order_id": order_id,
                    "sku": sku,
                    "decision": "rejected",
                    "code": exc.code,
                }
            )
            return rpc_error(exc.code, exc.message)
        except RpcServerError as exc:
            logging.error("Order %s failed: %s", order_id, exc.message)
            await self.add_context(
                {
                    "order_id": order_id,
                    "sku": sku,
                    "decision": "rejected",
                    "code": exc.code,
                }
            )
            raise

        logging.info("Order %s accepted", order_id)
        await self.add_context(
            {"order_id": order_id, "sku": sku, "decision": "accepted"}
        )
        return reservation


class Checkout:
    name = "Checkout"
    delegate = CheckoutDelegate()
    messenger = Messenger()

    @rpc
    async def place_order(self, order_id, sku, qty):
        return await self.delegate.place_order(order_id, sku, qty)
