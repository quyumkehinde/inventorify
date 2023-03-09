from sqlalchemy import String, Integer, Column, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    user = relationship('User', back_populates='products')
    category = relationship('Category', back_populates='products')

    def __repr__(self):
        return f'<Product(id={self.id}, name={self.name}, user_id={self.user_id}, category_id={self.category_id})>'


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    business_name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    products = relationship('Product', back_populates='user')
    categories = relationship('Category', back_populates='user')

    # def __getitem__(self, field):
    #     if field == 'courses':
    #         return self.courses
    #     return self.__dict__[field]
    def __repr__(self):
        return f'<User(id={self.id}, name={self.business_name}, email={self.email})>'


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='categories')
    products = relationship('Product', back_populates='category')

    def __repr__(self):
        return f'<Category(id={self.id}, name={self.name}, user_id={self.user_id})>'
