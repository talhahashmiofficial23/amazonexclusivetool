from django.contrib import admin
from .models import AmazonExclusive

@admin.register(AmazonExclusive)
class AmazonExclusiveAdmin(admin.ModelAdmin):
    list_display = (
        "article_color_name", "master_season", "year", "dept_div", "category",
    "subclass", "style_number", "style_desc", "color_desc", "size_desc",
    "multipack_qty", "variant_number", "upc", "asin", "current_status",
    "list_price", "planned_discount", "planned_asp", "merch_like_styles"
    )
    search_fields = ("style_number", "asin", "upc", "article_color_name")
    list_filter = ("year", "category", "current_status")
