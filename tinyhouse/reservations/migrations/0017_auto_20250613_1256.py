from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('reservations', '0016_auto_20250613_1250'),
    ]
    operations = [
        migrations.RunSQL(
            open('reservations/sql/procedures.sql', encoding='utf-8').read()
        ),
    ]
