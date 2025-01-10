from flask import request, url_for, jsonify
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_login import login_user, current_user, logout_user
from werkzeug.utils import redirect
from saleapp import utils
from saleapp.models import *
from saleapp import app


class AuthenticatedView(BaseView):
    def is_accessible(self):
        print(current_user)
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)

class CategoryModel(ModelView,AuthenticatedView):
    form_columns = ('name','products')

class ProductModel(ModelView,AuthenticatedView):
    pass;

# Overriden index page with my own view class
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('/admin/index.html',category_stats=utils.category_stats())
    @expose('/admin-login', methods=['post'])
    def admin_signin(self):
        err_msg = ''
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login(username=username, password=password,role=UserRole.ADMIN)
        if user:
            login_user(user)  # ghi nhan trang thai dang nhap -> bay gio co the su dung bien toan cuc current_user trong moi template
            print('Da dang nhap thanh cong')
            return redirect('/admin')
        else:
            err_msg = 'Username hoac password dang bi sai hoac ban khong co quyen truy cap'
            return self.render('/admin/index.html', err_msg=err_msg)


class LogOutView(AuthenticatedView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(AuthenticatedView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        year = request.args.get('year', datetime.now().year) # Neu co gui year len thi lay khong thi lay nam hien tai
        return self.render('admin/stats.html',
                           stats=utils.products_stats(kw=kw,from_date=from_date,to_date=to_date),
                           month_stats=utils.products_month_stats(year=year))

    @expose('/api/month_stats', methods=['post'])
    def analyze_month_stats(self):
        year = request.json.get('year')
        month_stats = utils.products_month_stats(year=year)
        month_stats = [tuple(row) for row in month_stats]
        print(month_stats)
        return jsonify(month_stats)


admin=Admin(app=app, name='Cua hang cong nghe', template_mode='bootstrap4',index_view=MyAdminIndexView())
admin.add_view(CategoryModel(Category,db.session))
admin.add_view(ProductModel(Product,db.session))
admin.add_view(ModelView(Tag,db.session))
admin.add_view(StatsView(name='Stat'))
admin.add_view(LogOutView(name='LogOut'))

# Tiep tuc lam thong ke theo thang dung Ajax


