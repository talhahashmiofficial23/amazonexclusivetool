# serializers.py

from rest_framework import serializers
from .models import AmazonExclusive, ProductPriceHistory

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class ProductPriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPriceHistory
        fields = ('id', 'amazon_exclusive', 'old_price', 'new_price', 'created_at')
        read_only_fields = ('id', 'created_at')


class CreateProductPriceHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new price history entry.
    If the AmazonExclusive doesn't exist, it will be created first.
    """
    product_data = serializers.DictField(
        write_only=True,
        required=False,
        help_text="Required if amazon_exclusive is not provided. Should contain fields for a new AmazonExclusive."
    )
    
    class Meta:
        model = ProductPriceHistory
        fields = ('amazon_exclusive', 'new_price', 'product_data')
        extra_kwargs = {
            'amazon_exclusive': {'required': False},  # Make this optional
            'new_price': {'required': True, 'min_value': 0}
        }
    
    def validate(self, attrs):
        amazon_exclusive = attrs.get('amazon_exclusive')
        product_data = attrs.pop('product_data', None)
        
        # If amazon_exclusive is not provided, we need product_data to create one
        if not amazon_exclusive and not product_data:
            raise serializers.ValidationError({
                'amazon_exclusive': 'Either provide an existing AmazonExclusive or product_data to create a new one'
            })
        
        return attrs
    
    def create(self, validated_data):
        amazon_exclusive = validated_data.get('amazon_exclusive')
        new_price = validated_data['new_price']
        product_data = validated_data.get('product_data', {})
        
        # If no amazon_exclusive provided, create a new one using product_data
        if not amazon_exclusive:
            # Set the list_price from the new_price if not provided
            if 'list_price' not in product_data:
                product_data['list_price'] = new_price
                
            # Create the AmazonExclusive with skip_price_history=True since we'll create it manually
            amazon_exclusive = AmazonExclusive.objects.create(
                **product_data,
                skip_price_history=True
            )
        
        # Get the old price before updating
        old_price = amazon_exclusive.list_price if amazon_exclusive.list_price is not None else Decimal('0')
        
        # Update the AmazonExclusive's current price with skip_price_history=True
        if amazon_exclusive.list_price != new_price:
            amazon_exclusive.list_price = new_price
            amazon_exclusive.save(skip_price_history=True)
        
        # Create a single price history entry
        price_history = ProductPriceHistory.objects.create(
            amazon_exclusive=amazon_exclusive,
            old_price=old_price,
            new_price=new_price
        )
        
        return price_history


class AmazonExclusiveSerializer(serializers.ModelSerializer):
    latest_price = serializers.SerializerMethodField(read_only=True)  # For latest price history
    price_history = serializers.SerializerMethodField(read_only=True)  # Will return only latest history

    def get_latest_price(self, obj):
        # Return the current price (same as list_price, but for consistency in API)
        return obj.list_price
        
    def get_price_history(self, obj):
        # Get only the latest price history for this product
        latest_history = obj.price_history.order_by('-created_at').first()
        if latest_history:
            return ProductPriceHistorySerializer(latest_history).data
        return None

    """Serializer for AmazonExclusive with custom cleaning for decimal fields.

    Incoming values for list_price (max_digits=50, decimal_places=2),
    planned_discount (max_digits=40, decimal_places=2) and planned_asp
    (max_digits=50, decimal_places=4) are cleaned:
        • Non-numeric or malformed values → 0
        • Values are quantized to the correct number of decimal places.
        • If the overall digit length exceeds max_digits after quantizing,
          the value is truncated to 0 to avoid DB errors.
    """

    def _clean_decimal(self, value, decimal_places, max_digits):
        if value in (None, ''):
            return Decimal('0')
        try:
            d = Decimal(str(value).replace(',', ''))
        except (InvalidOperation, ValueError):
            return Decimal('0')
        # Quantize to required decimal places
        quant = Decimal('1').scaleb(-decimal_places)  # e.g. Decimal('0.01')
        d = d.quantize(quant, rounding=ROUND_HALF_UP)
        # Check total digits (digits before + after the decimal point)
        digits_total = len(d.as_tuple().digits)
        if d.as_tuple().sign:
            digits_total -= 1  # sign doesn't count
        if digits_total > max_digits:
            return Decimal('0')
        return d

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs['list_price'] = self._clean_decimal(attrs.get('list_price'), 2, 50)
        attrs['planned_discount'] = self._clean_decimal(attrs.get('planned_discount'), 2, 40)
        attrs['planned_asp'] = self._clean_decimal(attrs.get('planned_asp'), 4, 50)
        return attrs
    class Meta:
        model = AmazonExclusive
        fields = '__all__'
        read_only_fields = ('price_history', 'latest_price')
        # Note: list_price remains writable for updates through the API