from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_tournament_addon_chips_tournament_buyin_chips_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='staff_chips',
            field=models.IntegerField(blank=True, default=0, help_text='Quantidade de fichas que o STAFF adiciona (se houver)', null=True),
        ),
        migrations.AddField(
            model_name='tournament',
            name='timechip_chips',
            field=models.IntegerField(blank=True, default=0, help_text='Quantidade de fichas do Time Chip', null=True),
        ),
        migrations.AddField(
            model_name='tournament',
            name='timechip_valor',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='Valor do Time Chip', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='tournamentproduct',
            name='chips_amount',
            field=models.IntegerField(blank=True, default=0, help_text='Quantidade de fichas que este produto adiciona ao jogo (0 ou vazio = não adiciona)', null=True),
        ),
    ]
