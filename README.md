# Kontiki example

Two Kontiki services over RabbitMQ: **Checkout** takes an order, **Inventory** reserves stock.

| Order | Request | Result |
| --- | --- | --- |
| `order-100` | 1 `MUG` | Accepted. Stock goes from 5 to 4, unit price 12. |
| `order-101` | 100 `MUG` | Rejected: `OUT_OF_STOCK`. |
| `order-102` | 1 `VASE` | Server error: the vase has no price. Inventory becomes degraded. |

Stock and prices live in memory in Inventory (`MUG` 5 @ 12, `VASE` 1, no price). A successful reserve publishes `stock.reserved`.

## Run

Open the repo in a dev container or GitHub Codespaces. The container starts RabbitMQ, the Kontiki registry, Checkout, and Inventory.

```bash
make example
kontiki-tui
```

`kontiki-tui` takes the terminal, so place the orders first. `make example` runs `place_orders.py` against `amqp://guest:guest@localhost/`. Service logs are in `/tmp/kontiki-registry.log`, `/tmp/inventory.log`, and `/tmp/checkout.log`. The RabbitMQ management UI is on port 15672 (`guest` / `guest`).
