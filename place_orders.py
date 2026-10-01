import asyncio

from kontiki.messaging import Messenger, RpcClientError, RpcProxy, RpcServerError
from kontiki.messaging.flow import generate_flow_id

# One mug in stock (5). The vase is on the shelf and has no price.
ORDERS = [
    ("order-100", "MUG", 1),
    ("order-101", "MUG", 100),
    ("order-102", "VASE", 1),
]


async def main():
    amqp_url = "amqp://guest:guest@localhost/"
    async with Messenger(amqp_url=amqp_url, standalone=True) as messenger:
        checkout = RpcProxy(messenger, service_name="Checkout")
        for order_id, sku, qty in ORDERS:
            print(f"Placing {order_id}: {qty} {sku}")
            try:
                result = await checkout.place_order(
                    order_id=order_id,
                    sku=sku,
                    qty=qty,
                    flow_id=generate_flow_id(),
                )
                print(f"  accepted: {result}")
            except RpcClientError as exc:
                print(f"  rejected: {exc.code} — {exc.message}")
            except RpcServerError as exc:
                print(f"  failed: {exc.code} — {exc.message}")


if __name__ == "__main__":
    asyncio.run(main())
