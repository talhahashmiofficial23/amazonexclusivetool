# serializers.py

from rest_framework import serializers
from .models import AmazonExclusive, ProductPriceHistory, MasterSeason, DepartmentDivision, Category, Subclass

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


class MasterSeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterSeason
        fields = '__all__'


class DepartmentDivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentDivision
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class SubclassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subclass
        fields = '__all__'


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


class NameRelatedField(serializers.Field):
    def __init__(self, model, **kwargs):
        self.model = model
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        # Accept either an integer (ID) or a string (name)
        if isinstance(data, int):
            try:
                return self.model.objects.get(pk=data)
            except self.model.DoesNotExist:
                raise serializers.ValidationError(f"No {self.model.__name__} found with id={data}.")
        elif isinstance(data, str):
            obj, _ = self.model.objects.get_or_create(name=data)
            return obj
        else:
            raise serializers.ValidationError('This field must be a string (name) or integer (id).')

    def to_representation(self, value):
        return value.name if value else None

class AmazonExclusiveSerializer(serializers.ModelSerializer):
    latest_price = serializers.SerializerMethodField(read_only=True)
    price_history = serializers.SerializerMethodField(read_only=True)
    master_season = NameRelatedField(model=MasterSeason, required=False, allow_null=True)
    dept_div = NameRelatedField(model=DepartmentDivision, required=False, allow_null=True)
    category = NameRelatedField(model=Category, required=False, allow_null=True)
    subclass = NameRelatedField(model=Subclass, required=False, allow_null=True)

    def get_latest_price(self, obj):
        return obj.list_price
    def get_price_history(self, obj):
        latest_history = obj.price_history.order_by('-created_at').first()
        if latest_history:
            return ProductPriceHistorySerializer(latest_history).data
        return None

    def _clean_decimal(self, value, decimal_places, max_digits):
        if value in (None, ''):
            return Decimal('0')
        try:
            d = Decimal(str(value).replace(',', ''))
        except (InvalidOperation, ValueError):
            return Decimal('0')
        quant = Decimal('1').scaleb(-decimal_places)
        d = d.quantize(quant, rounding=ROUND_HALF_UP)
        digits_total = len(d.as_tuple().digits)
        if d.as_tuple().sign:
            digits_total -= 1
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
