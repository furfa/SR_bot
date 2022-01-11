# Generated by Django 4.0.1 on 2022-01-11 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_accounts', '0012_rename_aditional_data_girlform_additional_data'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='girlform',
            options={'verbose_name': 'Анкеты', 'verbose_name_plural': 'Анкеты'},
        ),
        migrations.AlterModelOptions(
            name='usersupportquestion',
            options={'verbose_name': 'Вопросы к администрации', 'verbose_name_plural': 'Вопросы к администрации'},
        ),
        migrations.AddField(
            model_name='girlform',
            name='price',
            field=models.DecimalField(decimal_places=10, default=None, max_digits=17, null=True, verbose_name='Стоимость'),
        ),
        migrations.AlterField(
            model_name='botuser',
            name='balance',
            field=models.DecimalField(decimal_places=10, default=0, max_digits=17, verbose_name='баланс'),
        ),
    ]