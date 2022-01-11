# Generated by Django 4.0.1 on 2022-01-11 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0013_alter_girlform_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='girlprofile',
            name='has_top_status',
        ),
        migrations.AddField(
            model_name='girlform',
            name='has_top_status',
            field=models.BooleanField(default=False, verbose_name='Есть топ статус'),
        ),
        migrations.AlterField(
            model_name='girlform',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=10, default=None, max_digits=17, null=True, verbose_name='Стоимость'),
        ),
    ]