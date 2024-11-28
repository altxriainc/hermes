from src.model import BaseModel
from src.fields import IntegerField, StringField
from src.relations import ManyToMany

class Role(BaseModel):
    id = IntegerField(primary_key=True)
    name = StringField()
    users = ManyToMany("User", pivot_table="user_roles")
