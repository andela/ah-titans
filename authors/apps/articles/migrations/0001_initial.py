<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
# Generated by Django 2.0.6 on 2018-08-08 14:26
=======
# Generated by Django 2.0.6 on 2018-08-07 15:42
>>>>>>> [Chore #59053966] Make migrations
=======
# Generated by Django 2.0.6 on 2018-08-08 15:42
>>>>>>> [Chore #59053966] fixed confilcts
=======
# Generated by Django 2.0.6 on 2018-08-09 07:14
>>>>>>> [Chore #59053966] added database tests

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(db_index=True, max_length=255)),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('body', models.TextField()),
                ('description', models.TextField()),
                ('image_url', models.URLField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> [Chore #59053966] fixed confilcts
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('body', models.TextField()),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
<<<<<<< HEAD
=======
>>>>>>> [Chore #59053966] Make migrations
=======
>>>>>>> [Chore #59053966] fixed confilcts
            name='Ratings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('counter', models.IntegerField(default=0)),
                ('stars', models.IntegerField()),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating', to='articles.Article')),
            ],
        ),
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> [Chore #59053966] fixed confilcts
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tag', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'ordering': ['-created_at', '-updated_at'],
                'abstract': False,
            },
        ),
<<<<<<< HEAD
=======
>>>>>>> [Chore #59053966] Make migrations
=======
>>>>>>> [Chore #59053966] fixed confilcts
    ]
