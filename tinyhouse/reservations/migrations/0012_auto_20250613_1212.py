from django.db import migrations
from django.db import models  # <–– أضفنا هذا الاستيراد

class Migration(migrations.Migration):
    dependencies = [
        ('reservations', '0011_auto_20250613_1205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='reservation_status',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('beklemede', 'beklemede'),
                    ('onayli',   'onayli'),
                    ('iptal',    'iptal'),
                ],
                default='beklemede',
            ),
        ),
    ]
