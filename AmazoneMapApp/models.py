# models.py

from django.db import models

from BaseModel.models import TimeStampedModel


from django.conf import settings

class AmazonExclusive(TimeStampedModel):
    article_color_name = models.CharField(max_length=100, null=True, blank=True)
    master_season = models.CharField(max_length=50, null=True, blank=True)
    year = models.IntegerField(default=1, null=True, blank=True)
    dept_div = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=100, null=True, blank=True)
    subclass = models.CharField(max_length=100, null=True, blank=True)
    style_number = models.CharField(max_length=50, null=True, blank=True)
    style_desc = models.CharField(max_length=255, null=True, blank=True)
    color_desc = models.CharField(max_length=100, null=True, blank=True)
    size_desc = models.CharField(max_length=20, null=True, blank=True)
    multipack_qty = models.IntegerField(default=0, null=True, blank=True)
    variant_number = models.CharField(max_length=50, null=True, blank=True)
    upc = models.CharField(max_length=20, null=True, blank=True)
    asin = models.CharField(max_length=20, null=True, blank=True)
    current_status = models.CharField(max_length=50, null=True, blank=True)
    list_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    planned_discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    planned_asp = models.DecimalField(max_digits=10, decimal_places=4, default=0.0)
    merch_like_styles = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='amazonexclusives_created', on_delete=models.SET_NULL, null=True, blank=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='amazonexclusives_modified', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.article_color_name
