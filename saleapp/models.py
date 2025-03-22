import os.path
import json

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, Boolean, DATETIME, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from saleapp import db
from datetime import datetime
from saleapp import app
from enum import Enum as UserEnum


class UserRole(UserEnum):
    ADMIN = 1
    USER = 2


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    email = Column(String(50))
    active = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    comments = relationship('Comment', backref='user', lazy=True)

    def __str__(self):
        return self.name


class Category(BaseModel):
    __tablename__ = 'category'
    __table_args__ = {'extend_existing': True}
    name = Column(String(20), nullable=False)
    products = relationship('Product', backref='category', lazy=True)

    def __str__(self):
        return self.name


class Product(BaseModel):
    __tablename__ = 'product'
    __table_args__ = {'extend_existing': True}
    name = Column(String(50), nullable=False)
    description = Column(String(255))
    price = Column(Float, default=0)
    image = Column(String(100))
    active = Column(Boolean, default=True)
    created_date = Column(DATETIME, default=datetime.now())
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)
    tags = relationship('Tag', secondary='product_tag', back_populates='products', lazy='subquery')
    comments = relationship('Comment', backref='product', lazy=True)

    def __str__(self):
        return self.name


product_tag = db.Table('product_tag', Column('product_id', ForeignKey('product.id'), primary_key=True), Column(
    'tag_id', ForeignKey('tag.id'), primary_key=True), extend_existing=True)


class Tag(BaseModel):
    __tablename__ = 'tag'
    __table_args__ = {'extend_existing': True}
    name = Column(String(50), nullable=False, unique=True)
    products = relationship('Product', secondary='product_tag', back_populates='tags', lazy=True)

    def __str__(self):
        return self.name


class Receipt(BaseModel):
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', backref='receipts')


class ReceiptDetail(db.Model):
    receipt_id = Column(Integer, ForeignKey('receipt.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    quantity = Column(Integer, default=0)
    price = Column(Float, default=0)
    receipt = relationship('Receipt', backref='products')
    product = relationship('Product', backref='receipts')


class Comment(BaseModel):
    content = Column(String(255), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return self.content


def read_json(path):
    with open(path, "r") as f:
        return json.load(f)


if __name__ == '__main__':
    with app.app_context():
        data = [{
            "name": "iPhone 7 Plus",
            "description": "Apple, 32GB, RAM: 3GB, iOS13",
            "price": 17000000,
            "image":
                "https://res.cloudinary.com/dxxwcby8l/image/upload/v1647056401/ipmsmnxjydrhpo21xrd8.jpg",
            "category_id": 1
        }, {
            "name": "iPad Pro 2020",
            "description": "Apple, 128GB, RAM: 6GB",
            "price": 37000000,
            "image":
                "https://res.cloudinary.com/dxxwcby8l/image/upload/v1646729533/zuur9gzztcekmyfenkfr.jpg",
            "category_id": 2
        }, {
            "name": "Galaxy Note 10 Plus",
            "description": "Samsung, 64GB, RAML: 6GB",
            "price": 24000000,
            "image":
                "https://res.cloudinary.com/dxxwcby8l/image/upload/v1647248722/r8sjly3st7estapvj19u.jpg",
            "category_id": 1
        }]


        for p in data:

            pro = Product(name=p.get('name'), description=p.get('description'), price=p.get('price'), image=p.get('image'),
                    category_id=1)

            db.session.add(pro)

        db.session.commit()