from .model import OrderLine, List

def allocate(line: OrderLine, batches: List[Batch]):
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.ref
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")

class OutOfStock(Exception):
    pass

def insert_order_line(session):
    session.execute("INSERT INTO order_lines (orderid, sku, qty)"
                    'VALUES ("order1", "GENERIC-SOFA", 12)')
    [[orderline_id]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"
    )
    return orderline_id

def insert_batch(session, batch_id):
    pass

