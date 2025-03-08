import os
import datetime
import openpyxl
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = 'Generate daily backup as an Excel file'

    def handle(self, *args, **kwargs):
        # Define backup directory
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Set backup file name with date
        filename = f"backup_{datetime.datetime.now().strftime('%Y-%m-%d')}.xlsx"
        file_path = os.path.join(backup_dir, filename)

        # Create an Excel workbook
        wb = openpyxl.Workbook()
        first_sheet = True  # To avoid creating an empty default sheet

        # List of apps to include in the backup
        apps_to_backup = ['exam', 'students', 'teachers', 'main']

        for app_label in apps_to_backup:
            app_models = apps.get_app_config(app_label).get_models()

            for model in app_models:
                queryset = model.objects.all()
                if not queryset.exists():
                    continue  # Skip empty models

                # Create a new sheet for each model
                if first_sheet:
                    ws = wb.active
                    ws.title = model.__name__
                    first_sheet = False
                else:
                    ws = wb.create_sheet(title=model.__name__)

                # Write headers dynamically
                headers = [field.name for field in model._meta.fields]
                ws.append(headers)

                # Write data dynamically
                for obj in queryset:
                    row_data = [getattr(obj, field) for field in headers]
                    ws.append(row_data)

        # Save the Excel file
        wb.save(file_path)
        self.stdout.write(self.style.SUCCESS(f"Backup saved: {file_path}"))
