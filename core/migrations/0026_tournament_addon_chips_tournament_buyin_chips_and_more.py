from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_tournament_current_level_order_tournament_is_paused_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='addon_chips',
            field=models.IntegerField(blank=True, default=0, help_text='Quantidade de fichas do add-on', null=True),
        ),
        migrations.AddField(
            model_name='tournament',
            name='buyin_chips',
            field=models.IntegerField(blank=True, default=0, help_text='Quantidade de fichas do buy-in inicial', null=True),
        ),
        migrations.AddField(
            model_name='tournament',
            name='rebuy_chips',
            field=models.IntegerField(blank=True, default=0, help_text='Quantidade de fichas do rebuy simples', null=True),
        ),
        migrations.AddField(
            model_name='tournament',
            name='rebuy_duplo_chips',
            field=models.IntegerField(blank=True, default=0, help_text='Quantidade de fichas do rebuy duplo', null=True),
        ),
    ]
