from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('reservations', '0019_auto_20250613_1434'),
    ]
    operations = [
        migrations.RunSQL(
            open('reservations/sql/procedures.sql', encoding='utf-8').read()
        ),
    ]
