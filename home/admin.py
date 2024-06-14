from django.contrib import admin
from .models import Category, SubCategory, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_category')

    def get_category(self, obj):
        return obj.category.name if obj.category else 'No Category Assigned'
    get_category.short_description = 'Category'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_subcategory', 'get_category')

    def get_subcategory(self, obj):
        return obj.subcategory.name if obj.subcategory else 'No Subcategory Assigned'
    get_subcategory.short_description = 'Subcategory'

    def get_category(self, obj):
        if obj.subcategory and obj.subcategory.category:
            return obj.subcategory.category.name
        return 'No Subcategory or Category Assigned'

    get_category.short_description = 'Category'
