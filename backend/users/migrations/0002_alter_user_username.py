# Generated by Django 3.2.3 on 2024-10-07 00:34

from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[users.validators.validate_username], verbose_name='Имя пользователя'),
        ),
    ]
