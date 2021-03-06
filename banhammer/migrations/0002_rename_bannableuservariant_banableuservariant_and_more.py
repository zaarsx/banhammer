# Generated by Django 4.0.4 on 2022-05-20 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('banhammer', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BannableUserVariant',
            new_name='BanableUserVariant',
        ),
        migrations.CreateModel(
            name='BanHammer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ban', models.BooleanField(blank=True, default=True)),
                ('channel', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='banhammer.banableuser')),
            ],
            options={
                'verbose_name': 'ban hammer',
            },
        ),
    ]
