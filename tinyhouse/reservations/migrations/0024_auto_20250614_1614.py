from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('reservations', '0023_auto_20250614_1550'),
    ]
    operations = [
        migrations.RunSQL(
            open('reservations/sql/procedures.sql', encoding='utf-8').read()
        ),
    ]
