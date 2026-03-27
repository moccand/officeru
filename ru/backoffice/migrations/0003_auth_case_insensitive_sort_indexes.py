from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("backoffice", "0002_ruexport"),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS idx_auth_user_username_lw ON auth_user (LOWER(username));"
                "CREATE INDEX IF NOT EXISTS idx_auth_user_last_name_lw ON auth_user (LOWER(last_name));"
                "CREATE INDEX IF NOT EXISTS idx_auth_user_first_name_lw ON auth_user (LOWER(first_name));"
                "CREATE INDEX IF NOT EXISTS idx_auth_user_email_lw ON auth_user (LOWER(email));"
                "CREATE INDEX IF NOT EXISTS idx_auth_group_name_lw ON auth_group (LOWER(name));"
            ),
            reverse_sql=(
                "DROP INDEX IF EXISTS idx_auth_user_username_lw;"
                "DROP INDEX IF EXISTS idx_auth_user_last_name_lw;"
                "DROP INDEX IF EXISTS idx_auth_user_first_name_lw;"
                "DROP INDEX IF EXISTS idx_auth_user_email_lw;"
                "DROP INDEX IF EXISTS idx_auth_group_name_lw;"
            ),
        ),
    ]
