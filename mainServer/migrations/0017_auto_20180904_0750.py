# Generated by Django 2.0.2 on 2018-09-04 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainServer', '0016_auto_20180904_0742'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sesja',
            name='nazwa',
            field=models.TextField(default='Nienazwana_2018-09-04 05:50:47.983027+00:00'),
        ),
    ]