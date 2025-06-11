from django.contrib import admin
from .models import AmazonExclusive

@admin.register(AmazonExclusive)
class AmazonExclusiveAdmin(admin.ModelAdmin):
    list_display = (
        "article_color_name", "master_season", "year", "dept_div", "category",
        "subclass", "style_number", "style_desc", "color_desc", "size_desc",
        "multipack_qty", "variant_number", "upc", "asin", "current_status",
        "list_price", "planned_discount", "planned_asp", "merch_like_styles",
        "created_by", "modified_by"
    )
    search_fields = ("style_number", "asin", "upc", "article_color_name", "created_by__username", "modified_by__username")
    list_filter = ("year", "category", "current_status", "created_by", "modified_by")
