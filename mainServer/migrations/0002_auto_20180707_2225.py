# Generated by Django 2.0.2 on 2018-07-07 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainServer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sesja',
            name='nazwa',
            field=models.TextField(default='Nienazwana_<django.db.models.fields.AutoField>__2018-07-07 20:25:42.186052+00:00'),
        ),
    ]
