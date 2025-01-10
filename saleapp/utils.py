from flask_login import current_user
from sqlalchemy import func
from saleapp import db, app
from saleapp.models import Category, Product, Tag, User, Receipt, ReceiptDetail, UserRole, Comment
import hashlib
from sqlalchemy.sql import extract


def load_categories():
    return Category.query.all()


def load_products(cateID=None, **kwargs):
    products = Product.query.filter(Product.active.__eq__(True))
    if cateID:
        products = products.filter(Product.category_id.__eq__(int(cateID)))

    for key in kwargs.keys():
        if (key == 'keyword' and kwargs[key]):
            products = products.filter(Product.name.contains(kwargs[key]))

        if (key == 'from_price' and kwargs[key]):
            products = products.filter(Product.price.__ge__(kwargs[key]))

        if (key == 'to_price' and kwargs[key]):
            products = products.filter(Product.price.__le__(kwargs[key]))

        if (key == 'page' and kwargs[key]):
            start = (kwargs['page'] - 1) * app.config['PAGE_SIZE']
            end = start + app.config['PAGE_SIZE']
            products = products.slice(start, end)

    return products.all()


def load_product_by_id(id):
    return db.session.get(Product, id)


def count_products():
    return Product.query.filter(Product.active.__eq__(True)).count()


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(), username=username.strip(), password=password,
                email=kwargs.get('email'), avatar=kwargs.get('avatar'))

    db.session.add(user)
    db.session.commit()


def check_login(username, password, role=UserRole.USER):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        return User.query.filter(User.username.__eq__(username.strip()), User.password.__eq__(password),
                                 User.user_role.__eq__(role)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)


def add_receipt(cart):
    if cart:
        receipt = Receipt(user=current_user)
        for p in cart.keys():
            if p != 'total_quantity' and p != 'total_amount':
                receipt_detail = ReceiptDetail(receipt=receipt, product_id=cart.get(p).get('id'),
                                               quantity=cart.get(p).get('quantity'), price=cart.get(p).get('price'))
                db.session.add(receipt_detail)

        # Them chi tiet hoa don vao trong CSDL
        db.session.commit()


def category_stats():
    return db.session.query(Category.id, Category.name, func.count(Product.id)).join(Product,
                                                                                     Product.category_id.__eq__(
                                                                                         Category.id), isouter=True) \
        .group_by(Category.id).all()


def products_stats(kw=None, from_date=None, to_date=None):
    p = db.session.query(Product.id, Product.name, func.sum(ReceiptDetail.quantity * ReceiptDetail.price)) \
        .join(ReceiptDetail, ReceiptDetail.product_id.__eq__(Product.id), isouter=True) \
        .join(Receipt, Receipt.id.__eq__(ReceiptDetail.receipt_id)).group_by(Product.id)

    if kw:
        p = p.filter(Product.name.contains(kw))

    if from_date:
        p = p.filter(Receipt.created_date.__ge__(from_date))

    if to_date:
        p = p.filter(Receipt.created_date.__le__(to_date))

    return p.all()


def products_month_stats(year):
    return db.session.query(extract('month', Receipt.created_date),
                            func.sum(ReceiptDetail.quantity * ReceiptDetail.price)) \
        .join(ReceiptDetail, ReceiptDetail.receipt_id.__eq__(Receipt.id)) \
        .filter(extract('year', Receipt.created_date).__eq__(year)).group_by(extract('month', Receipt.created_date)) \
        .order_by(extract('month', Receipt.created_date)).all()

def add_comment(content, product_id, user_id):
    if content:
        c = Comment(content=content, product_id=product_id, user_id=user_id)
        db.session.add(c)
        db.session.commit()
        return c


def get_comment_by_products(product_id,page=1):
    start = (page-1) * app.config['COMMENT_SIZE']
    end = start + app.config['COMMENT_SIZE']
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).order_by(-Comment.id).slice(start,end).all()

def count_comments(product_id):
    return Comment.query.filter(Comment.product_id.__eq__(product_id)).count()

if __name__ == '__main__':
    print(app.root_path)
