# Generated by Django 3.0.7 on 2020-06-30 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music_entries', '0003_auto_20200630_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='musicentry',
            name='public_key',
            field=models.CharField(default='abcd', max_length=8),
            preserve_default=False,
        ),
    ]
