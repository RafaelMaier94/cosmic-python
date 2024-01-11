from datetime import date, timedelta

import pytest
from .local import insert_order_line, allocate, insert_batch, OutOfStock
from .model import Batch, OrderLine
import repository
# My implementation
# def test_allocating_to_a_batch_reduces_quantity():
#     sku = Sku("chair")
#     order_line = OrderLine(sku, 10)
#     order = Order("123", [order_line])
#     batch = Batch("batch-001", sku, qty=25, eta=date.today())
#     Batch.allocate(order_line)

#     assert Batch.quantity == 15

# Book implementation

def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine("order-123", sku, line_qty),
    )

def test_allocating_to_a_batch_reduces_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    allocate(line, [batch])

    assert batch.available_quantity == 18

def test_can_allocate_if_available_greather_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)

def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMPA", 2, 20)
    assert small_batch.can_allocate(large_line) is False

def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)

def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
    assert batch.can_allocate(different_sku_line) is False

def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20

def test_allocations_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    allocate(line, [batch])
    allocate(line, [batch])
    assert batch.available_quantity == 18

def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", 'RETRO-CLOCK', 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=date.today())
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity==90
    assert shipment_batch.available_quantity==100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=date.today())
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=date.today() + timedelta(1))
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=date.today() + timedelta(2))
    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=date.today().__add__(1))
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.ref

def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=date.today())
    allocate(OrderLine("order1", "SMALL-FORK", 10), [batch])

    with pytest.raises(OutOfStock, match="SMALL-FORK"):
        allocate(OrderLine("order2", "SMALL-FORK", 1), [batch])

def test_repository_can_save_a_batch(session):
    batch = Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = session.execte('SELECT reference, sku, _purchased_quantity, eta FROM batches')
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]

def test_repository_can_retrieve_a_batch_with_allocations(session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        OrderLine("order1", "GENERIC-SOFA", 12)
    }