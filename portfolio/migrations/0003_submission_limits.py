from django.db import migrations, models


def protect_database_tables(apps, schema_editor):
    connection = schema_editor.connection
    if connection.vendor != "postgresql":
        return

    with connection.cursor() as cursor:
        cursor.execute("SELECT current_schema()")
        schema = cursor.fetchone()[0]
        cursor.execute("SELECT rolname FROM pg_roles WHERE rolname IN ('anon', 'authenticated')")
        api_roles = [schema_editor.quote_name(row[0]) for row in cursor.fetchall()]

    tables = (
        "auth_group",
        "auth_group_permissions",
        "auth_permission",
        "auth_user",
        "auth_user_groups",
        "auth_user_user_permissions",
        "django_content_type",
        "django_migrations",
        "django_session",
        "portfolio_contactmessage",
        "portfolio_project",
        "portfolio_projectimage",
        "portfolio_submissionlimit",
    )
    qualified_tables = ", ".join(
        f"{schema_editor.quote_name(schema)}.{schema_editor.quote_name(table)}"
        for table in tables
    )
    roles = ", ".join(["PUBLIC", *api_roles])
    schema_editor.execute(f"REVOKE ALL PRIVILEGES ON TABLE {qualified_tables} FROM {roles}")


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("portfolio", "0002_project_repository_url"),
        ("sessions", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubmissionLimit",
            fields=[
                ("key", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("count", models.PositiveIntegerField(default=0)),
                ("expires_at", models.DateTimeField(db_index=True)),
            ],
        ),
        migrations.RunPython(protect_database_tables, migrations.RunPython.noop),
    ]
