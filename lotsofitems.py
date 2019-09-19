from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///applicationwithuser.db')
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


## Create Users

# Create dummy user

User1 = User(name="Jerry Seinfield", email="jerrys@gmail.com",
             picture='')
session.add(User1)
session.commit()


# Populate Categories and Items

## Items for Soccer

category1 = Category(name="Soccer Category", user_id=1)

session.add(category1)
session.commit()

Item1 = Item(name="Soccer Ball Name", description="Soccer Ball Item Description", category=category1, user_id=1)
session.add(Item1)
session.commit()

Item2 = Item(name="Soccer T-Shirt Name", description="Soccer T-Shirt Item Description", category=category1, user_id=1)
session.add(Item2)
session.commit()

Item3 = Item(name="Soccer Shorts Name", description="Soccer Shorts Item Description", category=category1, user_id=1)
session.add(Item3)
session.commit()

Item4 = Item(name="Soccer Shinguards Name", description="Soccer Shinguards Item Description", category=category1, user_id=1)
session.add(Item3)
session.commit()

# Items for Basket Ball
category2 = Category(name="Basket Ball Category", user_id=1)

session.add(category2)
session.commit()

Item5 = Item(name="Basket Ball Name", description="Basket Ball Item Description", category=category2, user_id=1)
session.add(Item5)
session.commit()

Item6 = Item(name="Basket Ball T-Shirt Name", description="Basket Ball T-Shirt Item Description", category=category2, user_id=1)
session.add(Item6)
session.commit()

Item7 = Item(name="Basket Ball Shorts Name", description="Basket Ball Shorts Item Description", category=category2, user_id=1)
session.add(Item7)
session.commit()

# Items for Frisbee
category3 = Category(name="Frisbee Category", user_id=1)

session.add(category3)
session.commit()

Item8 = Item(name="Frisbee Name", description="Light Frisbee Item Description", category=category3, user_id=1)
session.add(Item8)
session.commit()





print "added category and items!"
