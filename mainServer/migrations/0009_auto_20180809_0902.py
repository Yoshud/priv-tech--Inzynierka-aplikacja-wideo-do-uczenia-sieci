# Generated by Django 2.0.2 on 2018-08-09 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainServer', '0008_auto_20180731_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sesja',
            name='nazwa',
            field=models.TextField(default='Nienazwana_2018-08-09 07:02:41.303128+00:00'),
        ),
        migrations.AlterField(
            model_name='zbiorydanych',
            name='testowy',
            field=models.ManyToManyField(blank=True, related_name='zbioryTestowy', to='mainServer.ObrazPoDostosowaniu'),
        ),
        migrations.AlterField(
            model_name='zbiorydanych',
            name='uczacy',
            field=models.ManyToManyField(related_name='zbioryUczacy', to='mainServer.ObrazPoDostosowaniu'),
        ),
        migrations.AlterField(
            model_name='zbiorydanych',
            name='walidacyjny',
            field=models.ManyToManyField(blank=True, related_name='zbioryWalidacyjny', to='mainServer.ObrazPoDostosowaniu'),
        ),
    ]