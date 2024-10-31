"""Meta table repository"""
from models.db.meta import MetaTable
from .base import BaseRepository

class MetaRepository(BaseRepository[MetaTable]):
    def __init__(self):
        super().__init__("meta_table", MetaTable)

meta_repository = MetaRepository() 