from django.db import migrations

def forwards(apps, schema_editor):
    Profile = apps.get_model('accounts', 'Profile')
    # استبدال القيم
    Profile.objects.filter(role='kiraci').update(role='tenant')
    Profile.objects.filter(role='ev_sahibi').update(role='owner')
    # القيم 'admin' تبقى كما هي

def backwards(apps, schema_editor):
    Profile = apps.get_model('accounts', 'Profile')
    # للرجوع
    Profile.objects.filter(role='tenant').update(role='kiraci')
    Profile.objects.filter(role='owner').update(role='ev_sahibi')

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
