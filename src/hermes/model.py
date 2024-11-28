import logging
from hermes.fields import Field
from hermes.relations import (
    MorphMany, MorphOne, Relation, ForeignKey,
    OneToOne, OneToMany, ManyToMany
)
from hermes.query_builder import QueryBuilder
from hermes.exceptions import (
    RelationNotFound, FieldValidationError, ModelNotFound, HermesException
)
from hermes.config import get_config

# Load configuration
config = get_config()
debug_mode = config.get('debug', False)
console_log = config.get('console_log', False)

# Configure logging
logger = logging.getLogger(__name__)
if console_log:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.WARNING)

class BaseModelMeta(type):
    def __new__(cls, name, bases, dct):
        fields = {}
        relations = {}
        for key, value in dct.items():
            if isinstance(value, Field):
                fields[key] = value
            elif isinstance(value, Relation):
                relations[key] = value
        dct["_fields"] = fields
        dct["_relations"] = relations
        return super().__new__(cls, name, bases, dct)

class BaseModel(metaclass=BaseModelMeta):
    """
    Base class for defining ORM models.

    Provides functionality for field management, database operations,
    and relationships between models.
    """
    _table_name = None
    _model_registry = {}

    def __init_subclass__(cls, **kwargs):
        """
        Automatically register subclasses in the model registry.
        """
        super().__init_subclass__(**kwargs)
        BaseModel._model_registry[cls.__name__.lower()] = cls

    def __init__(self, **kwargs):
        # Initialize fields
        for field_name, field in self._fields.items():
            value = kwargs.get(field_name, field.default)
            try:
                field.validate(value)
            except FieldValidationError as e:
                if console_log:
                    logger.error(f"Validation error on field '{field_name}': {e}")
                if debug_mode:
                    raise
            setattr(self, field_name, value)

        # Initialize relationships
        for relation_name in self._relations:
            setattr(self, relation_name, None)

    def get_relation(self, relation_name, db_connection):
        """
        Retrieve a related model instance based on the specified relation.

        :param relation_name: Name of the relation.
        :param db_connection: Database connection object.
        :return: Related model instance or `None`.
        """
        if relation_name not in self._relations:
            message = f"Relation '{relation_name}' not found in model '{self.__class__.__name__}'."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationNotFound(message)
            return None

        relation = self._relations[relation_name]
        related_model = self._resolve_relation_model(relation)

        if isinstance(relation, ForeignKey):
            foreign_key_value = getattr(self, relation.foreign_key_field)
            return related_model.find(db_connection, foreign_key_value)
        elif isinstance(relation, OneToOne):
            return self.get_has_one(relation_name, db_connection)
        elif isinstance(relation, OneToMany):
            return self.get_has_many(relation_name, db_connection)
        elif isinstance(relation, ManyToMany):
            return self.get_many_to_many(db_connection, relation_name)
        elif isinstance(relation, MorphOne):
            return self.get_morph_one(relation_name, db_connection)
        elif isinstance(relation, MorphMany):
            return self.get_morph_many(relation_name, db_connection)
        else:
            message = f"Unsupported relation type for '{relation_name}'."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationNotFound(message)
            return None

    def get_has_one(self, relation_name, db_connection):
        """
        Retrieve the related model instance in a OneToOne relationship.

        :param relation_name: Name of the OneToOne relation.
        :param db_connection: Database connection object.
        :return: Related model instance or `None`.
        """
        if relation_name not in self._relations:
            message = f"Relation '{relation_name}' not found in model '{self.__class__.__name__}'."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationNotFound(message)
            return None

        relation = self._relations[relation_name]
        if not isinstance(relation, OneToOne):
            message = f"Relation '{relation_name}' is not a OneToOne relationship."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise ValueError(message)
            return None

        related_model = self._resolve_relation_model(relation)
        foreign_key_value = self._get_primary_key()

        query = f"""
        SELECT * FROM {related_model.get_table_name()}
        WHERE {relation.foreign_key_field} = ?
        LIMIT 1
        """
        try:
            result = db_connection.execute_sync(query, (foreign_key_value,))
            if result:
                return related_model(**dict(zip(related_model._fields.keys(), result[0])))
        except HermesException as e:
            if console_log:
                logger.error(f"Error fetching related model: {e}")
            if debug_mode:
                raise
        return None

    def get_has_many(self, relation_name, db_connection):
        """
        Retrieve related model instances in a OneToMany relationship.

        :param relation_name: Name of the OneToMany relation.
        :param db_connection: Database connection object.
        :return: List of related model instances.
        """
        if relation_name not in self._relations:
            message = f"Relation '{relation_name}' not found in model '{self.__class__.__name__}'."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationNotFound(message)
            return []

        relation = self._relations[relation_name]
        if not isinstance(relation, OneToMany):
            message = f"Relation '{relation_name}' is not a OneToMany relationship."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise ValueError(message)
            return []

        related_model = self._resolve_relation_model(relation)
        foreign_key_value = self._get_primary_key()

        query = f"""
        SELECT * FROM {related_model.get_table_name()}
        WHERE {relation.foreign_key_field} = ?
        """
        try:
            results = db_connection.execute_sync(query, (foreign_key_value,))
            return [related_model(**dict(zip(related_model._fields.keys(), row))) for row in results]
        except HermesException as e:
            if console_log:
                logger.error(f"Error fetching related models: {e}")
            if debug_mode:
                raise
        return []

    @classmethod
    def _resolve_relation_model(cls, relation):
        """
        Resolve the related model class from the relation.

        :param relation: Relation instance.
        :return: Related model class.
        """
        if isinstance(relation.related_model, str):
            related_model = BaseModel._model_registry.get(relation.related_model.lower())
            if not related_model:
                message = (
                    f"Model '{relation.related_model}' not found in the registry. "
                    f"Ensure the model is imported before accessing relationships."
                )
                if console_log:
                    logger.error(message)
                if debug_mode:
                    raise ModelNotFound(message)
                return None
            return related_model
        return relation.related_model

    @classmethod
    def get_primary_key(cls):
        """
        Get the primary key field name for the model.

        :return: The name of the primary key field.
        """
        for field_name, field in cls._fields.items():
            if field.primary_key:
                return field_name
        message = f"No primary key defined for the model {cls.__name__}."
        if console_log:
            logger.error(message)
        if debug_mode:
            raise ValueError(message)
        return None

    def _get_primary_key(self):
        """
        Get the primary key value for the current instance.

        :return: The primary key value.
        """
        primary_key_field = self.get_primary_key()
        if primary_key_field is None:
            return None
        return getattr(self, primary_key_field)

    @classmethod
    def get_table_name(cls):
        """
        Returns the table name for the model.

        If `_table_name` is not explicitly defined, the class name in lowercase is used.
        """
        return cls._table_name or cls.__name__.lower()

    def __repr__(self):
        """
        String representation of the model instance.

        Displays all fields and their values.
        """
        fields = ", ".join(f"{name}={repr(getattr(self, name))}" for name in self._fields)
        return f"<{self.__class__.__name__}({fields})>"

    @classmethod
    def all(cls, db_connection):
        """
        Retrieve all instances of the model from the database.

        Uses caching to improve performance for repeated queries.

        :param db_connection: Database connection object.
        :return: List of model instances.
        """
        query = QueryBuilder.select(cls)
        try:
            results = db_connection.execute_with_cache(query)
            return [cls(**dict(zip(cls._fields.keys(), row))) for row in results]
        except HermesException as e:
            if console_log:
                logger.error(f"Error retrieving all instances: {e}")
            if debug_mode:
                raise
        return []

    def save(self, db_connection):
        """
        Save or update the model instance in the database.

        Automatically performs an `INSERT` or `UPDATE` operation based on whether the
        primary key field is already present in the database.

        :param db_connection: Database connection object.
        """
        table_name = self.get_table_name()
        primary_key_field = self.get_primary_key()
        primary_key_value = getattr(self, primary_key_field, None)

        if primary_key_value is None:
            message = "Primary key must be set to save the instance."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise ValueError(message)
            return

        # Validate fields
        for field_name, field in self._fields.items():
            value = getattr(self, field_name)
            try:
                field.validate(value)
            except FieldValidationError as e:
                if console_log:
                    logger.error(f"Validation error on field '{field_name}': {e}")
                if debug_mode:
                    raise

        # Check existence
        check_query = f"SELECT 1 FROM {table_name} WHERE {primary_key_field} = ?"
        try:
            cursor = db_connection.connect_sync().execute(check_query, (primary_key_value,))
            exists = cursor.fetchone()

            if exists:
                # Update operation
                update_query, params = QueryBuilder.update(self)
                db_connection.connect_sync().execute(update_query, params)
                if console_log:
                    logger.info(f"Updated instance in table '{table_name}' with ID {primary_key_value}.")
            else:
                # Insert operation
                insert_query, params = QueryBuilder.insert(self)
                db_connection.connect_sync().execute(insert_query, params)
                if console_log:
                    logger.info(f"Inserted new instance into table '{table_name}' with ID {primary_key_value}.")
            db_connection.connect_sync().commit()
            db_connection.invalidate_cache()
        except HermesException as e:
            if console_log:
                logger.error(f"Error saving instance: {e}")
            if debug_mode:
                raise

    @classmethod
    def find(cls, db_connection, primary_key_value):
        """
        Find and return a single instance by primary key.

        :param db_connection: Database connection object.
        :param primary_key_value: The primary key value to search for.
        :return: An instance of the model or `None` if not found.
        """
        table_name = cls.get_table_name()
        primary_key_field = cls.get_primary_key()

        query = f"SELECT * FROM {table_name} WHERE {primary_key_field} = ?"
        try:
            results = db_connection.execute_sync(query, (primary_key_value,))
            if results:
                return cls(**dict(zip(cls._fields.keys(), results[0])))
        except HermesException as e:
            if console_log:
                logger.error(f"Error finding instance with ID {primary_key_value}: {e}")
            if debug_mode:
                raise
        return None

    def delete(self, db_connection):
        """
        Delete the model instance from the database.

        :param db_connection: Database connection object.
        """
        table_name = self.get_table_name()
        primary_key_field = self.get_primary_key()
        primary_key_value = self._get_primary_key()

        if primary_key_value is None:
            message = "Cannot delete instance without a primary key value."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise ValueError(message)
            return

        query = f"DELETE FROM {table_name} WHERE {primary_key_field} = ?"
        try:
            db_connection.connect_sync().execute(query, (primary_key_value,))
            db_connection.connect_sync().commit()
            db_connection.invalidate_cache()
            if console_log:
                logger.info(f"Deleted instance from table '{table_name}' with ID {primary_key_value}.")
        except HermesException as e:
            if console_log:
                logger.error(f"Error deleting instance: {e}")
            if debug_mode:
                raise

    def sync_many_to_many(self, db_connection, relation_name, related_ids):
        """
        Sync Many-to-Many relationships by replacing the current associations with new ones.

        :param db_connection: Database connection object.
        :param relation_name: Name of the ManyToMany relation.
        :param related_ids: List of IDs to associate.
        """
        if relation_name not in self._relations:
            message = f"Relation '{relation_name}' does not exist on {self.__class__.__name__}."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise ValueError(message)
            return

        relation = self._relations[relation_name]
        if not isinstance(relation, ManyToMany):
            message = f"Relation '{relation_name}' is not a Many-To-Many relationship."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise ValueError(message)
            return

        pivot_table = relation.pivot_table
        related_model = self._resolve_relation_model(relation)

        local_column = self.get_table_name() + "_id"
        related_column = related_model.get_table_name() + "_id"

        try:
            # Clear existing relationships
            db_connection.connect_sync().execute(
                f"DELETE FROM {pivot_table} WHERE {local_column} = ?", (self._get_primary_key(),)
            )

            # Insert new relationships
            for related_id in related_ids:
                db_connection.connect_sync().execute(
                    f"INSERT INTO {pivot_table} ({local_column}, {related_column}) VALUES (?, ?)",
                    (self._get_primary_key(), related_id)
                )
            db_connection.connect_sync().commit()
            if console_log:
                logger.info(f"Synced ManyToMany relation '{relation_name}' for instance ID {self._get_primary_key()}.")
        except HermesException as e:
            if console_log:
                logger.error(f"Error syncing ManyToMany relation: {e}")
            if debug_mode:
                raise

    def add_many_to_many(self, db_connection, relation_name, related_id):
        """
        Add a single association in a ManyToMany relationship.

        :param db_connection: Database connection object.
        :param relation_name: Name of the ManyToMany relation.
        :param related_id: ID of the related model to associate.
        """
        if relation_name not in self._relations:
            message = f"Relation '{relation_name}' does not exist on {self.__class__.__name__}."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationNotFound(message)
            return

        relation = self._relations[relation_name]
        if not isinstance(relation, ManyToMany):
            message = f"Relation '{relation_name}' is not a ManyToMany relationship."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise ValueError(message)
            return

        related_model = self._resolve_relation_model(relation)
        pivot_table = relation.pivot_table

        local_column = self.get_table_name() + "_id"
        related_column = related_model.get_table_name() + "_id"

        try:
            db_connection.connect_sync().execute(
                f"INSERT OR IGNORE INTO {pivot_table} ({local_column}, {related_column}) VALUES (?, ?)",
                (self._get_primary_key(), related_id)
            )
            db_connection.connect_sync().commit()
            if console_log:
                logger.info(f"Added association in ManyToMany relation '{relation_name}' for instance ID {self._get_primary_key()} with related ID {related_id}.")
        except HermesException as e:
            if console_log:
                logger.error(f"Error adding to ManyToMany relation: {e}")
            if debug_mode:
                raise

    def remove_many_to_many(self, db_connection, relation_name, related_id):
        """
        Remove a single association in a ManyToMany relationship.

        :param db_connection: Database connection object.
        :param relation_name: Name of the ManyToMany relation.
        :param related_id: ID of the related model to disassociate.
        """
        if relation_name not in self._relations:
            message = f"Relation '{relation_name}' does not exist on {self.__class__.__name__}."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationNotFound(message)
            return

        relation = self._relations[relation_name]
        if not isinstance(relation, ManyToMany):
            message = f"Relation '{relation_name}' is not a ManyToMany relationship."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise ValueError(message)
            return

        related_model = self._resolve_relation_model(relation)
        pivot_table = relation.pivot_table

        local_column = self.get_table_name() + "_id"
        related_column = related_model.get_table_name() + "_id"

        try:
            db_connection.connect_sync().execute(
                f"DELETE FROM {pivot_table} WHERE {local_column} = ? AND {related_column} = ?",
                (self._get_primary_key(), related_id)
            )
            db_connection.connect_sync().commit()
            if console_log:
                logger.info(f"Removed association in ManyToMany relation '{relation_name}' for instance ID {self._get_primary_key()} with related ID {related_id}.")
        except HermesException as e:
            if console_log:
                logger.error(f"Error removing from ManyToMany relation: {e}")
            if debug_mode:
                raise

    def get_many_to_many(self, db_connection, relation_name):
        """
        Retrieve related model instances in a ManyToMany relationship.

        :param db_connection: Database connection object.
        :param relation_name: Name of the ManyToMany relation.
        :return: List of related model instances.
        """
        if relation_name not in self._relations:
            message = f"Relation '{relation_name}' does not exist on {self.__class__.__name__}."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationNotFound(message)
            return []

        relation = self._relations[relation_name]
        if not isinstance(relation, ManyToMany):
            message = f"Relation '{relation_name}' is not a ManyToMany relationship."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise ValueError(message)
            return []

        related_model = self._resolve_relation_model(relation)
        pivot_table = relation.pivot_table
        related_table = related_model.get_table_name()

        local_column = self.get_table_name() + "_id"
        related_column = related_model.get_table_name() + "_id"

        query = (
            f"SELECT {related_table}.* FROM {related_table} "
            f"INNER JOIN {pivot_table} ON {pivot_table}.{related_column} = {related_table}.{related_model.get_primary_key()} "
            f"WHERE {pivot_table}.{local_column} = ?"
        )

        try:
            results = db_connection.execute_sync(query, (self._get_primary_key(),))
            return [related_model(**dict(zip(related_model._fields.keys(), row))) for row in results]
        except HermesException as e:
            if console_log:
                logger.error(f"Error retrieving ManyToMany relations: {e}")
            if debug_mode:
                raise
        return []

    def get_morph_one(self, relation_name, db_connection):
        """
        Retrieve the related model instance in a MorphOne relationship.

        :param relation_name: Name of the MorphOne relation.
        :param db_connection: Database connection object.
        :return: Related model instance or `None`.
        """
        if relation_name not in self._relations:
            message = f"Relation '{relation_name}' does not exist on {self.__class__.__name__}."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationNotFound(message)
            return None

        relation = self._relations[relation_name]
        if not isinstance(relation, MorphOne):
            message = f"Relation '{relation_name}' is not a MorphOne relationship."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise ValueError(message)
            return None

        related_model = self._resolve_relation_model(relation)
        morph_type = self.get_table_name()
        morph_id = self._get_primary_key()

        query = f"""
        SELECT * FROM {related_model.get_table_name()}
        WHERE {relation.morph_type_field} = ? AND {relation.morph_id_field} = ?
        LIMIT 1
        """

        try:
            result = db_connection.execute_sync(query, (morph_type, morph_id))
            if result:
                return related_model(**dict(zip(related_model._fields.keys(), result[0])))
        except HermesException as e:
            if console_log:
                logger.error(f"Error retrieving MorphOne relation: {e}")
            if debug_mode:
                raise
        return None

    def get_morph_many(self, relation_name, db_connection):
        """
        Retrieve related model instances in a MorphMany relationship.

        :param relation_name: Name of the MorphMany relation.
        :param db_connection: Database connection object.
        :return: List of related model instances.
        """
        if relation_name not in self._relations:
            message = f"Relation '{relation_name}' does not exist on {self.__class__.__name__}."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationNotFound(message)
            return []

        relation = self._relations[relation_name]
        if not isinstance(relation, MorphMany):
            message = f"Relation '{relation_name}' is not a MorphMany relationship."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise ValueError(message)
            return []

        related_model = self._resolve_relation_model(relation)
        morph_type = self.get_table_name()
        morph_id = self._get_primary_key()

        query = f"""
        SELECT * FROM {related_model.get_table_name()}
        WHERE {relation.morph_type_field} = ? AND {relation.morph_id_field} = ?
        """

        try:
            results = db_connection.execute_sync(query, (morph_type, morph_id))
            return [related_model(**dict(zip(related_model._fields.keys(), row))) for row in results]
        except HermesException as e:
            if console_log:
                logger.error(f"Error retrieving MorphMany relations: {e}")
            if debug_mode:
                raise
        return []

