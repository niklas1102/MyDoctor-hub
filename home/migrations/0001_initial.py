# Generated by Django 4.2.9 on 2025-04-09 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.URLField()),
                ('info', models.CharField(max_length=255)),
            ],
        ),
    ]
