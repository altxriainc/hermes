from src.model import BaseModel
from src.fields import IntegerField, StringField, ForeignKeyField
from src.relations import ForeignKey

class Profile(BaseModel):
    id = IntegerField(primary_key=True)
    user_id = ForeignKeyField(nullable=False, unique=True)  
    bio = StringField(nullable=True)
