"""Read-only schema comparison; does not create, fake or apply migrations."""
import json
from django.apps import apps
from django.db import connection
from django.db.migrations.loader import MigrationLoader

with connection.cursor() as cursor:
    existing = set(connection.introspection.table_names(cursor))
    missing = []
    missing_columns = []
    for model in apps.get_models():
        opts = model._meta
        if opts.proxy or not opts.managed:
            continue
        table = opts.db_table
        if table not in existing:
            missing.append({'app': opts.app_label, 'model': opts.object_name, 'table': table})
            continue
        cols = {c.name for c in connection.introspection.get_table_description(cursor, table)}
        for field in opts.local_fields:
            if field.column not in cols:
                missing_columns.append({'table': table, 'model': opts.label, 'column': field.column})
loader = MigrationLoader(connection)
app_labels = sorted({m._meta.app_label for m in apps.get_models()})
no_migrations = [a for a in app_labels if a not in loader.migrated_apps]
unapplied = sorted([f'{app}.{name}' for app, name in loader.graph.leaf_nodes() if (app, name) not in loader.applied_migrations])
result = {'missing_tables': missing, 'missing_columns': missing_columns, 'apps_without_migrations': no_migrations, 'unapplied_leaf_migrations': unapplied}
print(json.dumps(result, indent=2))
if missing or missing_columns or no_migrations or unapplied:
    print('NOT READY: Review schema and migration history before accepting orders.')
else:
    print('BASIC SCHEMA CHECK PASSED; indexes, constraints, and end-to-end flows still require validation.')
