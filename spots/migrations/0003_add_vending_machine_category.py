from django.db import migrations

CATEGORY = {
    "name": "自販機",
    "icon_class": "🥤",
    "color": "#EA580C",
    "student_registrable": True,
}


def add_category(apps, schema_editor):
    Category = apps.get_model("spots", "Category")
    Category.objects.update_or_create(name=CATEGORY["name"], defaults=CATEGORY)


def remove_category(apps, schema_editor):
    Category = apps.get_model("spots", "Category")
    Category.objects.filter(name=CATEGORY["name"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("spots", "0002_seed_categories"),
    ]

    operations = [
        migrations.RunPython(add_category, remove_category),
    ]
