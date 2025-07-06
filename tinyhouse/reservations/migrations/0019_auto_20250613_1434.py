from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('reservations', '0018_auto_20250613_1432'),
    ]
    operations = [
        migrations.RunSQL(
            open('reservations/sql/procedures.sql', encoding='utf-8').read()
        ),
    ]
