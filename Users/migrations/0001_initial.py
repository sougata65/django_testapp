# Generated by Django 3.1 on 2020-08-08 10:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('realname', models.CharField(max_length=512)),
                ('tz', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='ActivityPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starttime', models.DateTimeField()),
                ('endtime', models.DateTimeField()),
                ('userid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Users.user')),
            ],
        ),
    ]
