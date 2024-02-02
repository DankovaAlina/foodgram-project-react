import csv
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag

DATA_SOURCES_FOR_MOVIE_DATABASE = [
    (Ingredient, '../data/ingredients.csv', ['name', 'measurement_unit']),
    (Tag, '../data/tags.csv', ['name', 'color', 'slug']),
]


class Command(BaseCommand):
    help = 'Заполняет базу данных данными из CSV-файлов'

    def handle(self, *args, **options):
        for model, csv_file, fieldnames in DATA_SOURCES_FOR_MOVIE_DATABASE:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, fieldnames)
                for row in reader:
                    model.objects.get_or_create(**row)
            self.stdout.write(self.style.SUCCESS(
                f'Данные из {csv_file} успешно загружены в базу данных'
            ))
        self.stdout.write(self.style.SUCCESS(
            'Все данные успешно загружены в базу данных!'
        ))
