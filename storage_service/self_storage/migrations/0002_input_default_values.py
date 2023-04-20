from django.db import migrations
import random

def test_values(apps, schema_editor):
    Box = apps.get_model('self_storage', 'Box')
    Size = apps.get_model('self_storage', 'Size')
    Warehouse = apps.get_model('self_storage', 'Warehouse')

    Size.objects.create(
        name=0.5
    )

    Size.objects.create(
        name=1.5
    )

    Size.objects.create(
        name=3
    )

    Size.objects.create(
        name=6
    )

    Size.objects.create(
        name=9
    )

    Size.objects.create(
        name=18
    )

    sizes = Size.objects.all()

    warehouse_names = [
        'Москва',
        'Одинцово',
        'Пушкино',
        'Люберцы',
        'Домодедово'
    ]

    addresses = [
        'ул. Рокотова, д. 15',
        'ул. Северная, д. 36',
        'ул. Строителей, д. 5',
        'ул. Советская, д. 88',
        'ул. Орджоникидзе, д. 29'
    ]

    for i in range(5):
        number_of_floors = random.randint(2, 5)
        boxes_per_floor = random.randint(5, 10)

        warehouse = Warehouse.objects.create(
            name=warehouse_names[i],
            address=addresses[i],
            number_of_floors=number_of_floors,
            boxes_per_floor=boxes_per_floor
        )

        box_number = 0

        for floor_numb in range(number_of_floors):
            for _ in range(boxes_per_floor):
                box_number += 1

                Box.objects.create(
                    name=f'Бокс №{box_number}',
                    warehouse=warehouse,
                    size=random.choice(sizes),
                    floor=floor_numb+1
                )

class Migration(migrations.Migration):

    dependencies = [
        ('self_storage', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(test_values)
    ]