class HermesException(Exception):
    """
    Base exception for the Hermes ORM.

    All other exceptions in the ORM should inherit from this class.
    """
    pass


class RelationNotFound(HermesException):
    """
    Raised when a relation is not defined correctly.

    This occurs when a referenced relationship is missing or invalid.
    """
    pass


class ModelNotFound(HermesException):
    """
    Raised when a requested model cannot be found.

    This might happen when attempting to query or relate a model that does not exist.
    """
    pass


class DatabaseConnectionError(HermesException):
    """
    Raised when there is an issue connecting to the database.

    This could indicate that the database file is missing, permissions are incorrect,
    or the connection parameters are invalid.
    """
    pass


class MigrationError(HermesException):
    """
    Raised when an error occurs during a migration.

    This might happen if a migration file is invalid or if applying a migration fails.
    """
    pass


class FieldValidationError(HermesException):
    """
    Raised when a field fails validation.

    This might happen when attempting to save or update a model with invalid data.
    """

    def __init__(self, field_name, message="Field validation failed"):
        """
        Initialize the exception.

        :param field_name: Name of the field that caused the validation error.
        :param message: Optional error message.
        """
        super().__init__(f"{message}: {field_name}")
        self.field_name = field_name


class QueryExecutionError(HermesException):
    """
    Raised when a query execution fails.

    This might happen due to syntax errors in the SQL or issues with the database state.
    """

    def __init__(self, query, message="Query execution failed"):
        """
        Initialize the exception.

        :param query: The SQL query that caused the error.
        :param message: Optional error message.
        """
        super().__init__(f"{message}: {query}")
        self.query = query


class CacheError(HermesException):
    """
    Raised when there is an issue with the caching system.

    This might occur when attempting to use or clear a cache that is invalid or unavailable.
    """
    pass


class ConfigurationError(HermesException):
    """
    Raised when there is an issue with the configuration settings.

    This could occur when required configuration keys are missing,
    values are of incorrect types, or during read/write errors.
    """
    pass

class QueryBuilderError(HermesException):
    """
    Raised when there is an issue with the query builder structure.
    """
    pass

class RelationError(HermesException):
    """
    Raised when there is an issue with the relationship system.
    """
    pass
