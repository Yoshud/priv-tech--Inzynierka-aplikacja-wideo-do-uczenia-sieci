# Generated by Django 2.2.1 on 2019-05-25 12:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainServer', '0032_auto_20190523_2037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pozycjapunktupocrop',
            name='obraz',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pozycja', to='mainServer.ObrazPoDostosowaniu'),
        ),
        migrations.AlterField(
            model_name='sesja',
            name='nazwa',
            field=models.TextField(default='Nienazwana_2019-05-25 12:32:25.602776+00:00'),
        ),
    ]