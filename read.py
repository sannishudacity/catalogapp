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

##----User Table ------

print "---- User Table Begin ----"
user = session.query(User).all()
for i in user:
    print str(i.id)+"-"+i.name+"-"+i.email
print "---- User Table End ----"
print "---- Category Table Begin ----"
category = session.query(Category).all()
for i in category:
    print str(i.id)+"-"+i.name+"-"+str(i.user_id)
print "---- Category Table End ----"
print "---- Item Table Begin ----"
item = session.query(Item).all()
for i in item:
    print str(i.id)+"-"+i.name+"-"+i.description+"-"+str(i.category_id)+"-"+str(i.user_id)
print "---- Item Table End ----"

delete_flag=0
if delete_flag==1:
    user = session.query(User).all()
    j=0
    for i in user:
        j+=1
        session.delete(i)
        session.commit()
    print "User Records Delted: "+str(j)

if delete_flag==1:
    category = session.query(Category).all()
    j=0
    for i in category:
        j+=1
        session.delete(i)
        session.commit()
    print "Category Records Delted: "+str(j)

if delete_flag==1:
    item = session.query(Item).all()
    j=0
    for i in item:
        j+=1
        session.delete(i)
        session.commit()
    print "Item Records Delted: "+str(j)

