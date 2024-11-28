import click
from src.database import DatabaseConnection
from src.migrations import MigrationManager
from src.config import get_config, update_config
from src.exceptions import (
    DatabaseConnectionError,
    MigrationError,
    HermesException,
)

# Load configuration
config = get_config()
db_path = config.get("database_path", "hermes.db")
debug_mode = config.get("debug", False)
console_log = config.get("console_log", True)

# Initialize database and migration manager
try:
    db = DatabaseConnection(db_path)
    migrations = MigrationManager(db)
except Exception as e:
    raise DatabaseConnectionError(f"Failed to connect to the database at '{db_path}': {e}")


@click.group()
def cli():
    """
    **Hermes ORM Command Line Interface**

    Provides tools for managing database migrations, configurations,
    and interactions with Hermes ORM.

    **Available Commands:**
    - **migrate**: Apply all pending migrations.
    - **rollback**: Revert the last batch of migrations.
    - **make_migration**: Create a new migration file.
    - **show_config**: Display the current configuration.
    - **set_config**: Update a specific configuration setting.
    - **reset**: Rollback all migrations and reapply them.

    **Example Usage:**
    ```
    hermes migrate
    hermes rollback
    hermes make_migration create_users_table create
    hermes show_config
    hermes set_config database_path my_database.db
    ```
    """
    if console_log:
        click.secho("Welcome to the Hermes ORM CLI", fg="cyan")


@cli.command()
def show_config():
    """
    **Display the Current Configuration**

    Outputs the current settings loaded from the configuration file.
    """
    try:
        current_config = get_config()
        click.secho("Current Configuration:", fg="cyan")
        for key, value in current_config.items():
            click.echo(f"  {key}: {value}")
    except HermesException as e:
        if console_log:
            click.secho(f"Error loading configuration: {e}", fg="red")
        if debug_mode:
            raise


@cli.command()
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    """
    **Update a Specific Configuration Setting**

    **Arguments:**
    - **KEY**: The configuration key to update.
    - **VALUE**: The new value for the configuration key.

    **Example:**
    ```
    hermes set_config database_path custom.db
    ```
    """
    try:
        update_config({key: value})
        if console_log:
            click.secho(f"Configuration updated: {key} = {value}", fg="green")
    except HermesException as e:
        if console_log:
            click.secho(f"Failed to update configuration: {e}", fg="red")
        if debug_mode:
            raise


@cli.command()
def migrate():
    """
    **Apply All Pending Migrations**

    Checks the migrations directory for new migration files and executes them.
    """
    if console_log:
        click.secho("Starting the migration process...", fg="cyan")
    try:
        migrations.apply_migrations()
        if console_log:
            click.secho("Migrations applied successfully!", fg="green")
    except MigrationError as e:
        if console_log:
            click.secho(f"Migration process failed: {e}", fg="red")
        if debug_mode:
            raise
    except HermesException as e:
        if console_log:
            click.secho(f"Hermes ORM error: {e}", fg="red")
        if debug_mode:
            raise


@cli.command()
def rollback():
    """
    **Rollback the Last Batch of Migrations**

    Reverts the last set of migrations applied in a single batch.
    """
    if console_log:
        click.secho("Starting the rollback process...", fg="cyan")
    try:
        migrations.rollback_last_batch()
        if console_log:
            click.secho("Rollback completed successfully!", fg="green")
    except MigrationError as e:
        if console_log:
            click.secho(f"Rollback process failed: {e}", fg="red")
        if debug_mode:
            raise
    except HermesException as e:
        if console_log:
            click.secho(f"Hermes ORM error: {e}", fg="red")
        if debug_mode:
            raise


@cli.command()
@click.argument("name")
@click.argument("operation_type", type=click.Choice(["create", "update", "delete"]))
def make_migration(name, operation_type):
    """
    **Create a New Migration File**

    **Arguments:**
    - **NAME**: The name of the migration (e.g., 'create_users_table').
    - **OPERATION_TYPE**: The type of operation ('create', 'update', 'delete').

    Generates a new migration file with a timestamped name and a pre-structured skeleton.

    **Example:**
    ```
    hermes make_migration create_users_table create
    ```
    """
    if console_log:
        click.echo(f"Creating migration: {name} with operation '{operation_type}'...")
    try:
        migrations.create_migration(name, operation_type)
        if console_log:
            click.secho("Migration file created successfully!", fg="green")
    except MigrationError as e:
        if console_log:
            click.secho(f"Failed to create migration: {e}", fg="red")
        if debug_mode:
            raise
    except HermesException as e:
        if console_log:
            click.secho(f"Hermes ORM error: {e}", fg="red")
        if debug_mode:
            raise


@cli.command()
def reset():
    """
    **Rollback All Migrations and Reapply Them**

    Useful for resetting the database during development.
    """
    if console_log:
        click.secho("Resetting the database...", fg="cyan")
    try:
        # Rollback all migrations
        while True:
            migrations.rollback_last_batch()
            remaining_migrations = db.connect_sync().execute(
                "SELECT COUNT(*) FROM migrations"
            ).fetchone()[0]
            if remaining_migrations == 0:
                break

        # Reapply all migrations
        migrations.apply_migrations()
        if console_log:
            click.secho("Database reset successfully!", fg="green")
    except MigrationError as e:
        if console_log:
            click.secho(f"Error during database reset: {e}", fg="red")
        if debug_mode:
            raise
    except HermesException as e:
        if console_log:
            click.secho(f"Hermes ORM error: {e}", fg="red")
        if debug_mode:
            raise


if __name__ == "__main__":
    try:
        cli()
    except HermesException as e:
        if console_log:
            click.secho(f"Command execution error: {e}", fg="red")
        if debug_mode:
            raise
