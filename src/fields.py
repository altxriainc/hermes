from .config import get_config
from .exceptions import FieldValidationError

# Load configuration
config = get_config()
debug_mode = config.get('debug', False)
console_log = config.get('console_log', True)

class Field:
    """
    Base class for defining fields in a model.

    Attributes:
    - field_type: The SQL data type of the field.
    - primary_key: Whether the field is a primary key.
    - nullable: Whether the field allows NULL values.
    - default: The default value for the field.
    - unique: Whether the field must have unique values.
    """

    def __init__(self, field_type, primary_key=False, nullable=True, default=None, unique=False):
        self.field_type = field_type
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.unique = unique

    def get_sql(self, field_name):
        """
        Generate the SQL definition for the field.

        :param field_name: The name of the field.
        :return: A string containing the SQL definition of the field.
        """
        sql = f"{field_name} {self.field_type}"
        if self.primary_key:
            sql += " PRIMARY KEY"
        if not self.nullable:
            sql += " NOT NULL"
        if self.unique:
            sql += " UNIQUE"
        if self.default is not None:
            sql += f" DEFAULT {repr(self.default)}"
        return sql

    def validate(self, value):
        """
        Validate the value assigned to the field.

        :param value: The value to validate.
        :raises FieldValidationError: If validation fails.
        """
        if not self.nullable and value is None:
            raise FieldValidationError(
                field_name='',
                message="This field cannot be null."
            )

    def __repr__(self):
        """
        String representation of the field.
        """
        return (
            f"<Field(type={self.field_type}, primary_key={self.primary_key}, "
            f"nullable={self.nullable}, default={self.default}, unique={self.unique})>"
        )


class StringField(Field):
    """
    A field for storing variable-length strings.

    Attributes:
    - max_length: The maximum length of the string.
    """

    def __init__(self, max_length=255, **kwargs):
        super().__init__(field_type=f"VARCHAR({max_length})", **kwargs)
        self.max_length = max_length

    def validate(self, value):
        super().validate(value)
        if value is not None and len(value) > self.max_length:
            raise FieldValidationError(
                field_name='',
                message=f"String exceeds maximum length of {self.max_length}."
            )


class IntegerField(Field):
    """
    A field for storing integer values.
    """

    def __init__(self, **kwargs):
        super().__init__(field_type="INTEGER", **kwargs)

    def validate(self, value):
        super().validate(value)
        if value is not None and not isinstance(value, int):
            raise FieldValidationError(
                field_name='',
                message="Value must be an integer."
            )


class ForeignKeyField(IntegerField):
    """
    A field for storing foreign key integer values.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class BooleanField(Field):
    """
    A field for storing boolean values.
    """

    def __init__(self, **kwargs):
        super().__init__(field_type="BOOLEAN", **kwargs)

    def validate(self, value):
        super().validate(value)
        if value is not None and not isinstance(value, bool):
            raise FieldValidationError(
                field_name='',
                message="Value must be a boolean."
            )


class FloatField(Field):
    """
    A field for storing floating-point values.
    """

    def __init__(self, **kwargs):
        super().__init__(field_type="REAL", **kwargs)

    def validate(self, value):
        super().validate(value)
        if value is not None and not isinstance(value, float):
            raise FieldValidationError(
                field_name='',
                message="Value must be a float."
            )


class DateField(Field):
    """
    A field for storing date values.
    """

    def __init__(self, **kwargs):
        super().__init__(field_type="DATE", **kwargs)

    def validate(self, value):
        super().validate(value)
        # Add validation for date format if needed


class DateTimeField(Field):
    """
    A field for storing date and time values.
    """

    def __init__(self, **kwargs):
        super().__init__(field_type="DATETIME", **kwargs)

    def validate(self, value):
        super().validate(value)
        # Add validation for datetime format if needed


class TextField(Field):
    """
    A field for storing large text data.
    """

    def __init__(self, **kwargs):
        super().__init__(field_type="TEXT", **kwargs)


class JSONField(Field):
    """
    A field for storing JSON data.
    """

    def __init__(self, **kwargs):
        super().__init__(field_type="JSON", **kwargs)

    def validate(self, value):
        super().validate(value)
