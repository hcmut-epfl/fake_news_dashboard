from flask import redirect, url_for

from flask_login import current_user

from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from sqlalchemy import null


class AdminMixin:

    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        if 'request' in kwargs:
            request = kwargs['request']
            return redirect(url_for('security.login', next=request.url))


class AdminView(AdminMixin, ModelView):
    pass


class HomeAdminView(AdminMixin, AdminIndexView):
    pass


class BaseModelView(ModelView):

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.generate_slug()
        return super().on_model_change(form, model, is_created)

class PostAdminView(AdminMixin, BaseModelView):
    form_columns = [
        'time',
        'text',
        'url',
        'comments_count',
        'reactions_count',
        'shares_count',
        'comments',
        'true_news',
        'claim_info'
    ]