# Generated by Django 5.2.1 on 2025-06-19 19:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AmazoneMapApp', '0004_alter_amazonexclusive_list_price_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductPriceHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('old_price', models.DecimalField(decimal_places=2, max_digits=50)),
                ('new_price', models.DecimalField(decimal_places=2, max_digits=50)),
                ('amazon_exclusive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_history', to='AmazoneMapApp.amazonexclusive')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
