# Generated by Django 2.0.4 on 2018-04-07 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('greeting_keyword', 'Greeting Keyword'), ('greeting_response', 'Greeting Response'), ('none_response', 'None Response'), ('comments_about_self', 'Comment about self'), ('self_verbs_with_noun_caps_plural', 'Self verbs with noun caps plural'), ('self_verbs_with_noun_lower', 'Self verbs with noun lower'), ('self_verbs_with_adjective', 'Self verbs with adjective')], max_length=64)),
                ('text', models.CharField(max_length=255)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
