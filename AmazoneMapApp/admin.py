from django.contrib import admin
from .models import AmazonExclusive, ProductPriceHistory

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


@admin.register(ProductPriceHistory)
class ProductPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('amazon_exclusive', 'old_price', 'new_price', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('amazon_exclusive__article_color_name', 'amazon_exclusive__style_number')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_select_related = ('amazon_exclusive',)
