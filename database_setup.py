from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

print ("Define User Class")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    def __repr__(self):
        return "<User(name='{}', email='{}', picture={})>"\
                .format(self.name, self.email, self.picture)

print ("Define Category Class")
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(User)
    def __repr__(self):
        return "<Category(name='{}', user_id='{}'>"\
                .format(self.name, self.user_id)

#SQLITE
#    @property
#    def serialize(self):
#        """Return object data in easily serializeable format"""
#        return {
#            'name': self.name,
#            'id': self.id,
#        }

print ("Define Item Class")
class Item(Base):
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(User)
    def __repr__(self):
        return "<Item(name='{}', description='{}', category_id='{}', user_id='{}'>"\
                .format(self.name, self.description, self.category_id, self.user_id)


#SQLITE
#    @property
#    def serialize(self):
#        """Return object data in easily serializeable format"""
#        return {
#            'name': self.name,
#            'description': self.description,
#            'id': self.id,
#        }

#SQLITE
#engine = create_engine('sqlite:///applicationwithuser.db')

# Scheme: "postgres+psycopg2://<USERNAME>:<PASSWORD>@<IP_ADDRESS>:<PORT>/<DATABASE_NAME>"

print ("Define Database_URI")
#DATABASE_URI = 'postgres+psycopg2://postgres:mypassword@3.229.33.82:5432/catalogdb'
DATABASE_URI = 'postgres+psycopg2://postgres:mypassword@127.0.0.1:5432/catalogdb'

print ("Create Engine")
engine = create_engine(DATABASE_URI)

print ("Create All")
Base.metadata.create_all(engine)
print ("Moving to Lots of items program")
