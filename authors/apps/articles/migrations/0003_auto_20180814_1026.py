# Generated by Django 2.0.6 on 2018-08-14 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_auto_20180814_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentedithistory',
            name='comment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Comment'),
        ),
    ]
