import abc

from sqlalchemy.orm import mapper, relationship, Column, Integer, MetaData, Table, String

import model  #(1)


metadata = MetaData()

order_lines = Table(  #(2)
    "order_lines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sku", String(255)),
    Column("qty", Integer, nullable=False),
    Column("orderid", String(255)),
)

...

def start_mappers():
    lines_mapper = mapper(model.OrderLine, order_lines)  #(3)

class AbstractRepository(abc.ABC):
    @abc.abstractmethod  #(1)
    def add(self, batch: model.Batch):
        raise NotImplementedError  #(2)

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError

class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()