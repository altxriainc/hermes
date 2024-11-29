import logging
from .config import get_config
from .exceptions import RelationError

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

class Relation:
    """
    Base class for defining relationships between models.
    
    Attributes:
        related_model: The model this relation is associated with.
    """
    def __init__(self, related_model):
        if not related_model:
            message = "A related model must be specified."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationError(message)
        self.related_model = related_model

    def __repr__(self):
        return f"<Relation(related_model={self.related_model})>"

class ForeignKey(Relation):
    """
    Represents a ForeignKey relation.
    
    Attributes:
        foreign_key_field: The field in the current model referencing the related model's primary key.
    """
    def __init__(self, related_model, foreign_key_field):
        super().__init__(related_model)
        if not foreign_key_field:
            message = "Foreign key field must be specified for ForeignKey relation."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationError(message)
        self.foreign_key_field = foreign_key_field

    def __repr__(self):
        return f"<ForeignKey(related_model={self.related_model}, foreign_key_field={self.foreign_key_field})>"

class OneToOne(Relation):
    """
    Represents a OneToOne relation.
    
    Attributes:
        foreign_key_field: The field in the related model referencing the current model's primary key.
    """
    def __init__(self, related_model, foreign_key_field):
        super().__init__(related_model)
        if not foreign_key_field:
            message = "Foreign key field must be specified for OneToOne relation."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationError(message)
        self.foreign_key_field = foreign_key_field

    def __repr__(self):
        return f"<OneToOne(related_model={self.related_model}, foreign_key_field={self.foreign_key_field})>"

class OneToMany(Relation):
    """
    Represents a OneToMany relation.
    
    Attributes:
        foreign_key_field: The field in the related model referencing the current model's primary key.
    """
    def __init__(self, related_model, foreign_key_field):
        super().__init__(related_model)
        if not foreign_key_field:
            message = "Foreign key field must be specified for OneToMany relation."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationError(message)
        self.foreign_key_field = foreign_key_field

    def __repr__(self):
        return f"<OneToMany(related_model={self.related_model}, foreign_key_field={self.foreign_key_field})>"

class ManyToMany(Relation):
    """
    Represents a ManyToMany relation.
    
    Attributes:
        pivot_table: The name of the pivot table for this ManyToMany relation.
    """
    def __init__(self, related_model, pivot_table):
        super().__init__(related_model)
        if not pivot_table:
            message = "A pivot table must be specified for a ManyToMany relation."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationError(message)
        self.pivot_table = pivot_table

    def __repr__(self):
        return f"<ManyToMany(related_model={self.related_model}, pivot_table={self.pivot_table})>"

class MorphOne(Relation):
    """
    Represents a MorphOne relation.
    
    Attributes:
        morph_type_field: The field in the related model indicating the type of the current model.
        morph_id_field: The field in the related model referencing the current model's primary key.
    """
    def __init__(self, related_model, morph_type_field, morph_id_field):
        super().__init__(related_model)
        if not morph_type_field or not morph_id_field:
            message = "Both morph_type_field and morph_id_field must be specified for MorphOne relation."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationError(message)
        self.morph_type_field = morph_type_field
        self.morph_id_field = morph_id_field

    def __repr__(self):
        return f"<MorphOne(related_model={self.related_model}, morph_type_field={self.morph_type_field}, morph_id_field={self.morph_id_field})>"

class MorphMany(Relation):
    """
    Represents a MorphMany relation.
    
    Attributes:
        morph_type_field: The field in the related model indicating the type of the current model.
        morph_id_field: The field in the related model referencing the current model's primary key.
    """
    def __init__(self, related_model, morph_type_field, morph_id_field):
        super().__init__(related_model)
        if not morph_type_field or not morph_id_field:
            message = "Both morph_type_field and morph_id_field must be specified for MorphMany relation."
            if console_log:
                logger.error(message)
            if debug_mode:
                raise RelationError(message)
        self.morph_type_field = morph_type_field
        self.morph_id_field = morph_id_field

    def __repr__(self):
        return f"<MorphMany(related_model={self.related_model}, morph_type_field={self.morph_type_field}, morph_id_field={self.morph_id_field})>"
