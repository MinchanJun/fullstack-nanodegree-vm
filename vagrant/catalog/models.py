import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

####
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)

    @property
    def serialize(self):
        """
        Return object data in easily serializeable format
        """
        return {
            'id': self.id,
            'name': self.name,
        }
class CategoryItem(Base):
    __tablename__ = 'category_item'

    id = Column(Integer, primary_key = True)
    name = Column(String(100), nullable = False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        """
        Return object data in easily serializeable format
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }
engine = create_engine('sqlite:///itemcatalogapp.db')

Base.metadata.create_all(engine)
