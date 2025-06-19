# models.py

from django.db import models
from django.conf import settings
from decimal import Decimal

from BaseModel.models import TimeStampedModel

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
    list_price = models.DecimalField(max_digits=50, decimal_places=2, default=0.0)
    planned_discount = models.DecimalField(max_digits=40, decimal_places=2, default=0.0)
    planned_asp = models.DecimalField(max_digits=50, decimal_places=4, default=0.0)
    merch_like_styles = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='amazonexclusives_created', on_delete=models.SET_NULL, null=True, blank=True)
    modified_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='amazonexclusives_modified', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        """Override save to trace list_price changes.

        Accepts extra kwargs:
        - skip_price_history: If True, skips creating price history (useful when updating from API)
        - changed_by: User who made the change
        """
        skip_price_history = kwargs.pop('skip_price_history', False)
        is_create = self.pk is None
        old_price = Decimal('0')
        
        if not is_create:
            original = AmazonExclusive.objects.filter(pk=self.pk).first()
            old_price = original.list_price if original else Decimal('0')
        
        super().save(*args, **kwargs)
        
        # Only create price history if not skipped and price actually changed
        if not skip_price_history and (is_create or old_price != self.list_price):
            ProductPriceHistory.objects.create(
                amazon_exclusive=self,
                old_price=old_price,
                new_price=self.list_price
            )

    def __str__(self):
        return self.article_color_name


class ProductPriceHistory(TimeStampedModel):
    """Keeps history of list_price changes for AmazonExclusive items."""
    amazon_exclusive = models.ForeignKey('AmazonExclusive', related_name='price_history', on_delete=models.CASCADE)
    old_price = models.DecimalField(max_digits=50, decimal_places=2)
    new_price = models.DecimalField(max_digits=50, decimal_places=2)

    def __str__(self):
        return f"{self.amazon_exclusive} | {self.old_price} → {self.new_price}"

