from django.contrib import admin
from .models import Product
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import get_objects_for_user

@admin.register(Product)
class ProductAdmin(GuardedModelAdmin):
    list_display = ('name',)

     # 判断当前用户是否有权限访问该模型的管理界面。
    def has_module_permission(self, request):
        if super().has_module_permission(request):
            return True
        # 当前用户在该模型上具有的对象权限，并判断是否存在任何对象权限。
        return self.get_model_objects(request).exists()

    # 获取在管理界面中显示的对象集合。
    def get_queryset(self, request): 
        if request.user.is_superuser:
            return super().get_queryset(request)
        # 获取当前用户在该模型上具有的对象权限，并返回相应的对象集合。
        data = self.get_model_objects(request)
        return data

    # 获取当前用户在该模型上具有的对象权限。
    def get_model_objects(self, request, action=None, klass=None):  
        opts = self.opts
        actions = [action] if action else ['view','edit','delete']
        klass = klass if klass else opts.model
        model_name = klass._meta.model_name
        return get_objects_for_user(user=request.user, perms=[f'{perm}_{model_name}' for perm in actions], klass=klass, any_perm=True)

    # 判断当前用户是否具有指定对象的指定权限。
    def has_permission(self, request, obj, action):
        opts = self.opts
        code_name = f'{action}_{opts.model_name}'
        if obj:
            return request.user.has_perm(f'{opts.app_label}.{code_name}', obj)
        else:
            return self.get_model_objects(request).exists()

    # 判断当前用户是否具有查看、修改、删除指定对象的权限。
    def has_view_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'view')

    def has_change_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'change')

    def has_delete_permission(self, request, obj=None):
        return self.has_permission(request, obj, 'delete')
