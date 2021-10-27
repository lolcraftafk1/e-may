from sqlalchemy import Column, Integer, Float, String, Boolean,ForeignKey, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import uuid, random

Base = declarative_base()

class Product(Base):
  __tablename__ = 'product'
  id = Column(Integer, primary_key=True)
  name = Column(String)
  price = Column(Float)
  description = Column(String)
  img = Column(String)

engine = create_engine('sqlite:///database.db?check_same_thread=False')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

def getAllProducts():
    return session.query(Product).all()

def createProduct(name, price, description, img):
    newProduct = Product(name = name, price = price, description = description, img = img)
    session.add(newProduct)
    session.commit()

def getProductByName(name):
    return session.query(Product).filter_by(name = name).first()

def getProductById(id):
    return session.query(Product).filter_by(id = id).first()

def getAllItems(cartId):
    class Cart(Base):
        __tablename__ = cartId
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True)
        name = Column(String)
        price = Column(Float)
        description = Column(String)
        img = Column(String)
        amount = Column(Integer)
    return session.query(Cart).all()

def addItem(cartId, id):
    if cartId == -1:
        cartId = random.randint(0, 10000)
    class Cart(Base):
        __tablename__ = cartId
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True)
        name = Column(String)
        price = Column(Float)
        description = Column(String)
        img = Column(String)
        amount = Column(Integer)
    if engine.dialect.has_table(engine.connect(), str(cartId)) != False:
        if session.query(Cart).filter_by(id = id).first() != None:
            session.query(Cart).filter_by(id=id).first().amount = session.query(Cart).filter_by(id=id).first().amount +1 
            session.commit()
        else :
            product = session.query(Product).filter_by(id=id).first()
            curCart = Cart(name = product.name, price = product.price, description = product.description, img = product.img, amount = 1)
            session.add(curCart)
            session.commit()
    else :
        Base.metadata.create_all(engine)
        product = session.query(Product).filter_by(id=id).first()
        curCart = Cart(name = product.name, price = product.price, description = product.description, img = product.img, amount = 1)
        session.add(curCart)
        session.commit()
    return cartId