from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Categories"


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "Subcategories"


class Article(models.Model):
    name = models.CharField(max_length=100)
    producer_name = models.CharField(max_length=100)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'producer_name')

    def __str__(self):
        return f"{self.name}, {self.producer_name}"
