from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('reservations', '0008_auto_20250612_2336'),
    ]
    operations = [
        migrations.RunSQL(
            open('reservations/sql/procedures.sql', encoding='utf-8').read()
        ),
    ]
