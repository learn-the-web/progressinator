# Generated by Django 2.1.1 on 2018-09-30 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progress_core', '0009_auto_20180929_2037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprogress',
            name='cheated',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AlterField(
            model_name='userprogress',
            name='signature',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
