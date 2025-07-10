# import json
# from django.core.management.base import BaseCommand
# from AmazoneMapApp.models import MasterSeason, DepartmentDivision, Category, Subclass
#
# class Command(BaseCommand):
#     help = 'Load initial data for DepartmentDivision, Category, and Subclass models'
#
#     def handle(self, *args, **options):
#         # Load Master Seasons
#         with open('master_sons.json', 'r') as f:
#             master_seasons = json.load(f)
#             for item in master_seasons:
#                 MasterSeason.objects.get_or_create(name=item['name'].strip())
#             self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(master_seasons)} master seasons'))
#
#         # Load Department Divisions
#         with open('depivs.json', 'r') as f:
#             dept_divs = json.load(f)
#             for item in dept_divs:
#                 DepartmentDivision.objects.get_or_create(name=item['name'].strip())
#             self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(dept_divs)} department divisions'))
#
#         # Load Categories
#         with open('categies.json', 'r') as f:
#             categories = json.load(f)
#             for item in categories:
#                 Category.objects.get_or_create(name=item['name'].strip())
#             self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(categories)} categories'))
#
#         # Load Subclasses
#         with open('subsses.json', 'r') as f:
#             subclasses = json.load(f)
#             for item in subclasses:
#                 Subclass.objects.get_or_create(name=item['name'].strip())
#             self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(subclasses)} subclasses'))
