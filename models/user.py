from src.model import BaseModel
from src.fields import IntegerField, StringField
from src.relations import MorphOne, OneToMany, OneToOne, ManyToMany

class User(BaseModel):
    id = IntegerField(primary_key=True)
    name = StringField()
    # Relationships
    posts = OneToMany("Post", foreign_key_field="user_id")
    roles = ManyToMany("Role", "user_roles")
    image = MorphOne("Image", "imageable_type", "imageable_id")
    profile = OneToOne("Profile", foreign_key_field="user_id")
