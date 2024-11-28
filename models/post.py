from src.model import BaseModel
from src.fields import IntegerField, StringField, ForeignKeyField
from src.relations import MorphMany, ForeignKey, OneToMany

class Post(BaseModel):
    id = IntegerField(primary_key=True)
    user_id = ForeignKeyField(nullable=False)  #
    content = StringField(nullable=False)
    # Relationships
    images = MorphMany("Image", "imageable_type", "imageable_id")
    comments = OneToMany("Comment", foreign_key_field="post_id")
