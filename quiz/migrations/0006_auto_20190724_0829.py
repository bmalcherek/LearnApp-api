# Generated by Django 2.2.3 on 2019-07-24 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0005_auto_20190723_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myquestions',
            name='last_rep_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='myquestions',
            name='next_rep_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]