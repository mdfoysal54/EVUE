from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder
from django.apps import apps

class Command(BaseCommand):
    help = "Report commerce schema migration and table readiness (read only)."

    def handle(self, *args, **options):
        apps_to_check = ("accounts", "catalog", "commerce", "operations")
        existing = set(connection.introspection.table_names())
        applied = set(MigrationRecorder(connection).applied_migrations())
        problems = 0
        for label in apps_to_check:
            config = apps.get_app_config(label)
            app_migrations = sorted(name for app, name in applied if app == label)
            self.stdout.write(f"{label}: applied migrations={app_migrations or 'NONE'}")
            for model in config.get_models():
                table = model._meta.db_table
                if table not in existing:
                    self.stderr.write(f"MISSING TABLE: {table}")
                    problems += 1
        if problems:
            self.stderr.write(f"NOT READY: {problems} missing tables. Do not accept orders.")
        else:
            self.stdout.write(self.style.SUCCESS("All registered application model tables exist."))