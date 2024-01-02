from datetime import date
from local import Batch, OrderLine
# My implementation
# def test_allocating_to_a_batch_reduces_quantity():
#     sku = Sku("chair")
#     order_line = OrderLine(sku, 10)
#     order = Order("123", [order_line])
#     batch = Batch("batch-001", sku, qty=25, eta=date.today())
#     Batch.allocate(order_line)

#     assert Batch.quantity == 15

# Book implementation


def test_allocating_to_a_batch_reduces_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18
