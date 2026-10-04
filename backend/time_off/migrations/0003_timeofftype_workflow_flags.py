from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [("time_off", "0002_initial")]

    operations = [
        migrations.AddField(
            model_name="timeoffrequest",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.AddField(
            model_name="timeofftype",
            name="requires_approval",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="timeoffrequest",
            name="created_at",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.AddField(
            model_name="timeofftype",
            name="affects_payroll",
            field=models.BooleanField(default=False),
        ),
    ]
