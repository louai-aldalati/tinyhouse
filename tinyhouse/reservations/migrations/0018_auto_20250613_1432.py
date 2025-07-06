from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('reservations', '0017_auto_20250613_1256'),
    ]
    operations = [
        migrations.RunSQL(
            open('reservations/sql/procedures.sql', encoding='utf-8').read()
        ),
    ]
