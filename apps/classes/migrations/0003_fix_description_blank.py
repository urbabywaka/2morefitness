from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0002_auto_20260208_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gymclass',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
