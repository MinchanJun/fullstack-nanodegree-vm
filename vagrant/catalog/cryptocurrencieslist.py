from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Category, CategoryItem

engine = create_engine('sqlite:///itemcatalogapp.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()




# Category for Bitcoin
category1 = Category(name="Bitcoin")

session.add(category1)
session.commit()

categoryitem1 = CategoryItem(name="Acronym", description="BTC",
                     category=category1)

session.add(categoryitem1)
session.commit()

categoryitem2 = CategoryItem(name="Price", description="$10,000",
                     category=category1)

session.add(categoryitem2)
session.commit()

categoryitem3 = CategoryItem(name="Details", description="Bitcoin is a digital \
                    currency created in 2009. It follows the ideas set out in  \
                    a white paper by the mysterious Satoshi Nakamoto.",
                     category=category1)

session.add(categoryitem3)
session.commit()

# Category for Ethereum
category2 = Category(name="Ethereum")

session.add(category2)
session.commit()

categoryitem1 = CategoryItem(name="Acronym", description="ETH",
                     category=category2)

session.add(categoryitem1)
session.commit()

categoryitem2 = CategoryItem(name="Price", description="$1,000",
                     category=category2)

session.add(categoryitem2)
session.commit()

categoryitem3 = CategoryItem(name="Details", description="At its simplest, \
                    Ethereum is an open software platform based on blockchain \
                    technology that enables developers to build and deploy \
                    decentralized applications.",
                     category=category2)

session.add(categoryitem3)
session.commit()




print "added menu items!"
