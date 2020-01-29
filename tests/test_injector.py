from injector import ClassProvider
from injector import Injector
from injector import Module
from injector import singleton
from sqlalchemy import String
from typing import Optional

from sqlalchemy.engine import Engine
from sqlar.repository import sqla_crud

from persipy import CRUDRepository
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper


class Fixture:
    def __init__(self):
        class MyEntity:
            def __init__(self, id_: int, name: Optional[str]):
                self.id = id_
                self.name = name

        engine = self._engine = create_engine('sqlite://')
        metadata = MetaData()
        my_entity_table = Table(
            'my_entities',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String),
        )
        mapper(MyEntity, my_entity_table)

        class MyRepository(CRUDRepository[MyEntity, int]):
            pass

        metadata.create_all(bind=self._engine)

        class Configuration(Module):
            def configure(self, binder):
                binder.bind(Engine, engine)
                binder.bind(MyRepository, to=ClassProvider(sqla_crud(MyRepository)), scope=singleton)

        configuration = Configuration()
        injector = Injector([configuration])
        self.repository = injector.get(MyRepository)

    def execute(self, sql):
        return self._engine.execute(sql)


def test_count():
    fixture = Fixture()
    fixture.execute('INSERT INTO my_entities (id) VALUES (1), (2), (3);')

    # Act
    count = fixture.repository.count()

    assert count == 3
