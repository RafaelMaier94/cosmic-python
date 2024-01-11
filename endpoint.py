import flask
from model import OrderLine, Batch
from repository import SqlAlchemyRepository
from local import allocate

@flask.route.gubbins
def allocate_endpoint():
    batches = SqlAlchemyRepository.list()
    lines = [
        OrderLine(l['orderid'], l['sku'], l['qty'])
         for l in flask.request.params...
    ]
    allocate(lines, batches)
    session.commit()
    return 201