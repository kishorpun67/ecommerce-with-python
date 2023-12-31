# Generated by Django 5.0 on 2023-12-11 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='email',
            field=models.EmailField(help_text='Email address of the user', max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='first_name',
            field=models.CharField(blank=True, help_text='First name of the user', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='last_name',
            field=models.CharField(blank=True, help_text='Last name of the user', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Phone number of the user', max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.CharField(blank=True, help_text='Username of the user', max_length=50, null=True, unique=True),
        ),
    ]
