import os
import datetime
import importlib.util
from .database import DatabaseConnection
from .fields import Field
from .config import get_config
from .exceptions import MigrationError, HermesException

# Load configuration
config = get_config()
debug_mode = config.get("debug", False)
console_log = config.get("console_log", True)
migrations_dir = config.get("migrations_dir", "migrations")

class MigrationAction:
    """
    Base class for migration actions.

    Subclasses must implement the `to_sql` method to generate the corresponding SQL statement.
    """
    def to_sql(self):
        raise NotImplementedError("Subclasses must implement `to_sql`.")

class RawSQL(MigrationAction):
    """
    Represents a raw SQL action.
    """
    def __init__(self, sql):
        self.sql = sql

    def to_sql(self):
        return self.sql

class CreateTable(MigrationAction):
    """
    Represents a SQL CREATE TABLE action.
    """
    def __init__(self, table_name, fields, constraints=None):
        """
        :param table_name: Name of the table to create.
        :param fields: Dictionary of fields where keys are column names and values are Field instances.
        :param constraints: Optional list of table-level constraints (e.g., FOREIGN KEY, PRIMARY KEY).
        """
        self.table_name = table_name
        self.fields = fields
        self.constraints = constraints or []

    def to_sql(self):
        field_definitions = []
        for name, field in self.fields.items():
            field_definitions.append(field.get_sql(name))

        # Append table-level constraints
        field_definitions.extend(self.constraints)

        return f"CREATE TABLE IF NOT EXISTS {self.table_name} ({', '.join(field_definitions)});"

class DropTable(MigrationAction):
    """
    Represents a SQL DROP TABLE action.
    """
    def __init__(self, table_name):
        self.table_name = table_name

    def to_sql(self):
        return f"DROP TABLE IF EXISTS {self.table_name};"

class AlterTable(MigrationAction):
    """
    Represents a SQL ALTER TABLE action.

    Attributes:
    - add_fields: A dictionary of fields to add.
    - drop_fields: A list of field names to drop.
    """
    def __init__(self, table_name, add_fields=None, drop_fields=None, add_constraints=None, drop_constraints=None):
        self.table_name = table_name
        self.add_fields = add_fields or {}
        self.drop_fields = drop_fields or []
        self.add_constraints = add_constraints or []
        self.drop_constraints = drop_constraints or []

    def to_sql(self):
        sql_statements = []
        for name, field in self.add_fields.items():
            sql_statements.append(f"ADD COLUMN {field.get_sql(name)}")
        for name in self.drop_fields:
            sql_statements.append(f"DROP COLUMN {name}")
        # Note: SQLite has limited support for altering constraints; additional logic may be needed.
        return f"ALTER TABLE {self.table_name} {', '.join(sql_statements)};"

class InsertData(MigrationAction):
    """
    Represents a SQL INSERT INTO action.

    Attributes:
    - data: A dictionary of column-value pairs to insert.
    """
    def __init__(self, table_name, data):
        self.table_name = table_name
        self.data = data

    def to_sql(self):
        columns = ", ".join(self.data.keys())
        values = ", ".join(f"'{value}'" for value in self.data.values())
        return f"INSERT INTO {self.table_name} ({columns}) VALUES ({values});"

class MigrationManager:
    """
    Manages database migrations, including creating, applying, and rolling back migrations.

    Attributes:
    - db: DatabaseConnection instance.
    - migrations_dir: Directory where migration files are stored.
    """
    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.migrations_dir = migrations_dir
        self.debug_mode = config.get("debug", False)
        self.console_log = config.get("console_log", True)

    def ensure_migrations_table(self):
        """
        Ensures the `migrations` table exists in the database.
        """
        try:
            connection = self.db.connect_sync()
            connection.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT NOT NULL,
                batch INTEGER NOT NULL
            )
            """)
            connection.commit()
            if self.console_log:
                print("Ensured migrations table exists.")
        except Exception as e:
            if self.console_log:
                print(f"Error ensuring migrations table: {e}")
            if self.debug_mode:
                raise MigrationError(f"Failed to ensure migrations table: {e}")

    def create_migration(self, name, operation_type="create"):
        """
        Create a new migration file with a skeleton structure.

        :param name: Name of the migration (e.g., 'create_users_table').
        :param operation_type: Type of operation ('create', 'update', 'delete').
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{name}.py"
            filepath = os.path.join(self.migrations_dir, filename)

            os.makedirs(self.migrations_dir, exist_ok=True)  # Ensure the directory exists
            skeleton = self.generate_migration_skeleton(name, operation_type)

            with open(filepath, "w") as file:
                file.write(skeleton)

            if self.console_log:
                print(f"Migration '{name}' created at {filepath}.")
        except Exception as e:
            if self.console_log:
                print(f"Error creating migration '{name}': {e}")
            if self.debug_mode:
                raise MigrationError(f"Failed to create migration '{name}': {e}")

    def generate_migration_skeleton(self, name, operation_type):
        """
        Generate the skeleton content for a migration file.

        :param name: Name of the migration.
        :param operation_type: Type of operation ('create', 'update', 'delete').
        :return: A string containing the migration skeleton.
        """
        table_name = name.split("_")[1]

        if operation_type == "create":
            up_code = f"""
    return [
        CreateTable("{table_name}", {{
            # Define your fields here
            "id": IntegerField(primary_key=True),
            "name": StringField(max_length=255, nullable=False),
            # Add more fields as needed
        }}, constraints=[
            # Add table-level constraints like FOREIGN KEYs here
        ])
    ]"""
            down_code = f"""
    return [
        DropTable("{table_name}")
    ]"""
        elif operation_type == "update":
            up_code = f"""
    return [
        AlterTable("{table_name}", add_fields={{
            # Add fields to add here
        }}, drop_fields=[
            # List fields to drop here
        ], add_constraints=[
            # Add new constraints here
        ], drop_constraints=[
            # List constraints to drop here
        ])
    ]"""
            down_code = "# Add your rollback actions for update operations here"
        elif operation_type == "delete":
            up_code = f"""
    return [
        DropTable("{table_name}")
    ]"""
            down_code = "# Add your rollback actions for delete operations here"
        else:
            raise ValueError("Invalid operation type. Must be 'create', 'update', or 'delete'.")

        return f"""
from altxria.hermes.migrations import CreateTable, DropTable, AlterTable
from altxria.hermes.fields import IntegerField, StringField, DateTimeField

def up():
    \"\"\"Apply the migration.\"\"\"
    {up_code}

def down():
    \"\"\"Rollback the migration.\"\"\"
    {down_code}
"""

    def get_executed_migrations(self):
        """
        Retrieve all executed migrations from the `migrations` table.
        """
        try:
            connection = self.db.connect_sync()
            cursor = connection.execute("SELECT migration_name FROM migrations")
            executed = {row[0] for row in cursor.fetchall()}
            if self.console_log:
                print(f"Executed migrations: {executed}")
            return executed
        except Exception as e:
            if self.console_log:
                print(f"Error retrieving executed migrations: {e}")
            if self.debug_mode:
                raise MigrationError(f"Failed to retrieve executed migrations: {e}")

    def get_migration_files(self):
        """
        Retrieve all migration files from the migrations directory.
        """
        try:
            files = os.listdir(self.migrations_dir)
            migration_files = sorted([f for f in files if f.endswith(".py")])
            if self.console_log:
                print(f"Migration files: {migration_files}")
            return migration_files
        except Exception as e:
            if self.console_log:
                print(f"Error retrieving migration files: {e}")
            if self.debug_mode:
                raise MigrationError(f"Failed to retrieve migration files: {e}")

    def apply_migrations(self):
        """
        Apply all pending migrations.
        """
        try:
            self.ensure_migrations_table()
            
            # Retrieve executed migrations and handle None case
            executed = self.get_executed_migrations()
            if executed is None:
                executed = set()  # Default to an empty set if None
            
            # Retrieve migration files and handle None case
            files = self.get_migration_files()
            if files is None:
                raise MigrationError("No migration files found in the migrations directory.")

            # Identify new migrations
            new_migrations = [f for f in files if f not in executed]
            if not new_migrations:
                if self.console_log:
                    print("No migrations to apply.")
                return

            # Apply new migrations
            connection = self.db.connect_sync()
            batch = self.get_next_batch_number()
            for file in new_migrations:
                if self.console_log:
                    print(f"Applying migration: {file}")
                module = self.load_migration(file)
                if not hasattr(module, 'up'):
                    raise MigrationError(f"The migration file '{file}' is missing the 'up()' function.")
                
                actions = module.up()
                self.execute_migration(connection, actions)
                connection.execute(
                    "INSERT INTO migrations (migration_name, batch) VALUES (?, ?)",
                    (file, batch)
                )
                connection.commit()

            if self.console_log:
                print("Migrations applied successfully.")

        except MigrationError as e:
            if self.console_log:
                print(f"Migration error: {e}")
            if self.debug_mode:
                raise
        except HermesException as e:
            if self.console_log:
                print(f"Error applying migrations: {e}")
            if self.debug_mode:
                raise
        except Exception as e:
            if self.console_log:
                print(f"An unexpected error occurred: {e}")
            if self.debug_mode:
                raise

    def rollback_last_batch(self):
        """
        Rollback the last batch of migrations.
        """
        try:
            self.ensure_migrations_table()
            connection = self.db.connect_sync()
            cursor = connection.execute("SELECT MAX(batch) FROM migrations")
            last_batch = cursor.fetchone()[0]

            if not last_batch:
                if self.console_log:
                    print("No migrations to rollback.")
                return

            cursor = connection.execute(
                "SELECT migration_name FROM migrations WHERE batch = ?",
                (last_batch,)
            )
            files = [row[0] for row in cursor.fetchall()]

            for file in reversed(files):
                if self.console_log:
                    print(f"Rolling back migration: {file}")
                module = self.load_migration(file)
                rollback_actions = module.down()
                self.rollback_migration(connection, rollback_actions)
                connection.execute("DELETE FROM migrations WHERE migration_name = ?", (file,))
                connection.commit()

            if self.console_log:
                print("Rollback completed.")
        except HermesException as e:
            if self.console_log:
                print(f"Error during rollback: {e}")
            if self.debug_mode:
                raise

    def get_next_batch_number(self):
        """
        Get the next batch number for migrations.

        :return: Next batch number as an integer.
        """
        try:
            connection = self.db.connect_sync()
            cursor = connection.execute("SELECT MAX(batch) FROM migrations")
            last_batch = cursor.fetchone()[0]
            next_batch = (last_batch or 0) + 1
            if self.console_log:
                print(f"Next batch number: {next_batch}")
            return next_batch
        except Exception as e:
            if self.console_log:
                print(f"Error getting next batch number: {e}")
            if self.debug_mode:
                raise MigrationError(f"Failed to get next batch number: {e}")

    def load_migration(self, file):
        """
        Dynamically load a migration module.

        :param file: Migration file name.
        :return: Loaded migration module.
        """
        try:
            migration_path = os.path.join(self.migrations_dir, file)
            spec = importlib.util.spec_from_file_location("migration_module", migration_path)
            migration_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(migration_module)
            if self.console_log:
                print(f"Loaded migration module from {migration_path}")
            return migration_module
        except Exception as e:
            if self.console_log:
                print(f"Error loading migration '{file}': {e}")
            if self.debug_mode:
                raise MigrationError(f"Failed to load migration '{file}': {e}")

    def execute_migration(self, connection, actions):
        """
        Execute a list of migration actions.

        :param connection: Database connection.
        :param actions: List of MigrationAction instances.
        """
        try:
            for action in actions:
                sql = action.to_sql()
                if self.console_log:
                    print(f"Executing SQL:\n{sql}")
                connection.execute(sql)
        except Exception as e:
            if self.console_log:
                print(f"Error executing migration actions: {e}")
            if self.debug_mode:
                raise MigrationError(f"Failed to execute migration actions: {e}")

    def rollback_migration(self, connection, rollback_actions):
        """
        Execute a list of rollback actions.

        :param connection: Database connection.
        :param rollback_actions: List of MigrationAction instances.
        """
        try:
            for action in reversed(rollback_actions):
                sql = action.to_sql()
                if self.console_log:
                    print(f"Executing SQL:\n{sql}")
                connection.execute(sql)
        except Exception as e:
            if self.console_log:
                print(f"Error executing rollback actions: {e}")
            if self.debug_mode:
                raise MigrationError(f"Failed to execute rollback actions: {e}")
