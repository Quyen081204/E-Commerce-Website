import math
from flask import render_template, request, redirect, url_for, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from saleapp import utils
from saleapp import app , login
import cloudinary.uploader

@app.route('/')
def home():
    cateID = request.args.get('category_id')
    page = request.args.get('page', 1)
    products = utils.load_products(cateID=cateID,keyword=request.args.get('keyword'),page=int(page))
    pages = math.ceil(utils.count_products()/app.config['PAGE_SIZE'])

    return render_template('index.html',products=products,pages=pages)

@app.route('/products')
def hienThiTatCaSp():
    products = utils.load_products(keyword=request.args.get('keyword'),from_price=request.args.get('from_price'),
                                   to_price=request.args.get('to_price'))
    return render_template('products.html',products=products)


@app.route('/products/<int:productID>')
def detailProducts(productID):
    product = utils.load_product_by_id(productID)
    page = int(request.args.get('page',1))
    comments = utils.get_comment_by_products(product_id=productID,page=page)
    pages = math.ceil(utils.count_comments(product_id=productID)/app.config['COMMENT_SIZE'])
    return render_template('detailProduct.html'
                           ,product=product,
                            comments=comments,
                            pages=pages
                           )

@app.route('/register', methods=['get','post'])
def user_register():
    err_msg = ''
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        confirm = request.form.get('confirm')
        avatar = request.files.get('avatar')
        avatar_url = None
        try:
            if password.strip().__eq__(confirm.strip()):
                if avatar:
                    res = cloudinary.uploader.upload(avatar) # upload anh dai dien len cloudinary
                    avatar_url = res['secure_url']# get url for the image uploaded
                utils.add_user(name=name,username=username,password=password,email=email,avatar=avatar_url)
                return redirect(url_for('user_signin'))
            else:
                err_msg = 'Mat khau nhap lai khong khop'
        except Exception as ex:
            err_msg = 'He thong dang bi loi ' + str(ex)

    return render_template('register.html', err_msg=err_msg)


@app.route('/user-login', methods=['get','post']) # get method just for viewing , post method for login
def user_signin():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login(username=username, password=password)
        if user:
            login_user(user) # ghi nhan trang thai dang nhap -> bay gio co the su dung bien toan cuc current_user trong moi template
            next = request.args.get('next')
            return redirect(request.args.get('next') or url_for('home'))
        else:
            err_msg = 'Username hoac password dang bi sai'

    return render_template('login.html',err_msg=err_msg)

@login.user_loader   # Duoc goi truoc moi request kiem tra what user_id in the current session and will reload that object by the ID
def load_user(user_id):
    return utils.get_user_by_id(user_id=user_id)  # return logged in user as current_user

@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))

@app.route('/api/add-cart', methods=['post'])
def add_product_to_shopping_cart():
    id = str(request.json.get('id'))
    name = request.json.get('name')
    price = request.json.get('price')

    cart = session.get('cart')
    if not cart:
        cart = {'total_amount': 0, 'total_quantity': 0}
    if id not in cart:
        cart[id] = {
            'id': id,
            'name': name,
            'price': price,
            'quantity': 1
        }
    else:
        cart[id]['quantity'] = cart[id]['quantity'] + 1

    cart['total_quantity'] = cart['total_quantity'] + 1
    cart['total_amount'] = cart['total_amount'] + price

    session['cart'] = cart

    return jsonify({'total_amount':cart['total_amount'] , 'total_quantity': cart['total_quantity']})


@app.route('/cart')
def load_cart():
    return render_template('cart.html')

@app.route('/api/pay', methods=['post'])
@login_required
def pay():
    try:
        utils.add_receipt(session.get('cart'))
        # Xoa san pham khoi session
        session.pop('cart', None)
    except:
        return jsonify({'code':404})

    return jsonify({'code':200})

@app.route('/api/update_cart', methods=['put'])
def update_cart():
    data = request.json
    id = str(data.get('id'))
    quantity = data.get('quantity')
    cart = session.get('cart')
    if id in cart:
        delta = quantity - cart[id]['quantity']
        cart[id]['quantity'] = quantity
        cart['total_quantity'] = cart['total_quantity'] + delta
        cart['total_amount'] = cart['total_amount'] + (delta * cart[id].get('price'))
        session['cart'] = cart

        return jsonify({'total_amount': cart['total_amount'], 'total_quantity': cart['total_quantity']})


@app.route('/api/remove_item', methods=['put'])
def remove_item_in_cart():
    id = str(request.json.get('id'))
    cart = session['cart']
    quantity = cart.get(id).get('quantity')
    unit_price = cart.get(id).get('price')
    cart['total_quantity'] -= quantity
    cart['total_amount'] -= (quantity * unit_price)
    # Xoa san pham khoi gio hang
    cart.pop(id)
    session['cart'] = cart

    return jsonify({'total_amount': cart['total_amount'], 'total_quantity': cart['total_quantity']})

@app.route('/api/add_comment', methods=['post'])
@login_required
def add_comment():
    data = request.json
    if data.get('content'):
        try:
            c = utils.add_comment(content=data.get('content'),product_id=data.get('product_id'),user_id=current_user.id)
        except:
            return jsonify({'status': 404, 'err_msg': 'Loi xu ly'})

        return jsonify({
            # Them binh luan thanh cong
            'status' : 201,
            'comment' : {
                'content' : c.content,
                'created_date': str(c.created_date),
                'user_name': c.user.username
            }
        })
    else:
        return jsonify({'status': 404, 'err_msg': 'Chua nhap binh luan'})

@app.route('/api/products/<int:product_id>/comments')
def load_comments(product_id):
    page = request.args.get('page',1)
    comments = utils.get_comment_by_products(product_id=product_id,page=int(page))
    result = []
    for c in comments:
        result.append({
            'comment' : {
                'content' : c.content,
                'created_date': str(c.created_date),
                'user_name': c.user.username
            }
        })

    return jsonify(result)




@app.context_processor
def common_response():
    cart_counter = 0
    if session.get('cart'):
        cart_counter = session.get('cart').get('total_quantity')

    return {
        'cates':utils.load_categories(),
        'cart_counter': cart_counter
    }

if __name__ == '__main__':
    with app.app_context():
        from saleapp.admin import *
        app.run(debug=True)


