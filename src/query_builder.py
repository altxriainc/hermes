import logging
from src.config import get_config
from src.exceptions import QueryBuilderError, HermesException

# Load configuration
config = get_config()
debug_mode = config.get('debug', False)
console_log = config.get('console_log', True)

# Configure logging
logger = logging.getLogger(__name__)
if console_log:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.WARNING)

class QueryBuilder:
    """
    A utility class for generating SQL queries dynamically.
    """

    @staticmethod
    def select(model_class, where=None, order_by=None, limit=None, offset=None):
        """
        Generate a SELECT query for a model.

        :param model_class: The model class to query.
        :param where: A dictionary of conditions for the WHERE clause.
        :param order_by: A string or list of columns to order the results by.
        :param limit: The maximum number of rows to return.
        :param offset: The number of rows to skip.
        :return: A tuple (SQL query string, parameters list).
        """
        try:
            table_name = model_class.get_table_name()
            fields = ", ".join(model_class._fields.keys())
            query = f"SELECT {fields} FROM {table_name}"
            params = []

            if where:
                conditions = " AND ".join([f"{k} = ?" for k in where.keys()])
                query += f" WHERE {conditions}"
                params.extend(where.values())

            if order_by:
                if isinstance(order_by, (list, tuple)):
                    order_by_clause = ", ".join(order_by)
                else:
                    order_by_clause = order_by
                query += f" ORDER BY {order_by_clause}"

            if limit is not None:
                query += f" LIMIT {limit}"
            if offset is not None:
                query += f" OFFSET {offset}"

            if console_log:
                logger.info(f"Generated SELECT query: {query}")

            return query, params
        except Exception as e:
            if console_log:
                logger.error(f"Error generating SELECT query: {e}")
            if debug_mode:
                raise QueryBuilderError(f"Failed to generate SELECT query: {e}")

    @staticmethod
    def insert(instance):
        """
        Generate an INSERT query for a model instance.

        :param instance: The model instance to insert.
        :return: A tuple (SQL query string, parameters list).
        """
        try:
            table_name = instance.get_table_name()
            fields = ", ".join(instance._fields.keys())
            placeholders = ", ".join("?" for _ in instance._fields.keys())
            params = [getattr(instance, field) for field in instance._fields.keys()]

            query = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"

            if console_log:
                logger.info(f"Generated INSERT query: {query}")

            return query, params
        except Exception as e:
            if console_log:
                logger.error(f"Error generating INSERT query: {e}")
            if debug_mode:
                raise QueryBuilderError(f"Failed to generate INSERT query: {e}")

    @staticmethod
    def update(instance):
        """
        Generate an UPDATE query for a model instance.

        :param instance: The model instance to update.
        :return: A tuple (SQL query string, parameters list).
        """
        try:
            table_name = instance.get_table_name()
            primary_key_field = instance.get_primary_key()

            if primary_key_field is None:
                message = "Instance must have a primary key to update."
                if console_log:
                    logger.error(message)
                if debug_mode:
                    raise ValueError(message)
                return None, None

            updates = ", ".join(f"{field} = ?" for field in instance._fields if field != primary_key_field)
            params = [getattr(instance, field) for field in instance._fields if field != primary_key_field]
            params.append(getattr(instance, primary_key_field))  # Add the WHERE clause parameter

            query = f"UPDATE {table_name} SET {updates} WHERE {primary_key_field} = ?"

            if console_log:
                logger.info(f"Generated UPDATE query: {query}")

            return query, params
        except Exception as e:
            if console_log:
                logger.error(f"Error generating UPDATE query: {e}")
            if debug_mode:
                raise QueryBuilderError(f"Failed to generate UPDATE query: {e}")

    @staticmethod
    def delete(instance):
        """
        Generate a DELETE query for a model instance.

        :param instance: The model instance to delete.
        :return: A tuple (SQL query string, parameters list).
        """
        try:
            table_name = instance.get_table_name()
            primary_key_field = instance.get_primary_key()

            if primary_key_field is None:
                message = "Instance must have a primary key to delete."
                if console_log:
                    logger.error(message)
                if debug_mode:
                    raise ValueError(message)
                return None, None

            query = f"DELETE FROM {table_name} WHERE {primary_key_field} = ?"
            params = [getattr(instance, primary_key_field)]

            if console_log:
                logger.info(f"Generated DELETE query: {query}")

            return query, params
        except Exception as e:
            if console_log:
                logger.error(f"Error generating DELETE query: {e}")
            if debug_mode:
                raise QueryBuilderError(f"Failed to generate DELETE query: {e}")

    @staticmethod
    def join(model_class, related_model, foreign_key, local_key, where=None):
        """
        Generate a JOIN query between two models.

        :param model_class: The main model class.
        :param related_model: The related model class.
        :param foreign_key: The foreign key in the related model.
        :param local_key: The primary key in the main model.
        :param where: A dictionary of conditions for the WHERE clause.
        :return: A tuple (SQL query string, parameters list).
        """
        try:
            main_table = model_class.get_table_name()
            related_table = related_model.get_table_name()
            query = (
                f"SELECT * FROM {main_table} "
                f"INNER JOIN {related_table} "
                f"ON {main_table}.{local_key} = {related_table}.{foreign_key}"
            )
            params = []

            if where:
                conditions = " AND ".join([f"{k} = ?" for k in where.keys()])
                query += f" WHERE {conditions}"
                params.extend(where.values())

            if console_log:
                logger.info(f"Generated JOIN query: {query}")

            return query, params
        except Exception as e:
            if console_log:
                logger.error(f"Error generating JOIN query: {e}")
            if debug_mode:
                raise QueryBuilderError(f"Failed to generate JOIN query: {e}")
