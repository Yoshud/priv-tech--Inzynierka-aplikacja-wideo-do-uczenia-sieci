# Generated by Django 2.2.1 on 2019-05-23 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainServer', '0031_auto_20190523_1956'),
    ]

    operations = [
        migrations.RenameField(
            model_name='parametryuczenia',
            old_name='opisUczeniaXML',
            new_name='opisUczeniaJSON',
        ),
        migrations.RenameField(
            model_name='sieci',
            old_name='opisXML',
            new_name='opisJSON',
        ),
        migrations.AlterField(
            model_name='sesja',
            name='nazwa',
            field=models.TextField(default='Nienazwana_2019-05-23 20:36:51.199301+00:00'),
        ),
    ]
