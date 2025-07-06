from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('reservations', '0013_fix_procedures_and_default'),
    ]
    operations = [
        migrations.RunSQL(
            open('reservations/sql/procedures.sql', encoding='utf-8').read()
        ),
    ]
