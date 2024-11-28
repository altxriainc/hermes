from src.model import BaseModel
from src.fields import IntegerField, StringField, ForeignKeyField
from src.relations import ForeignKey

class Comment(BaseModel):
    id = IntegerField(primary_key=True)
    post_id = ForeignKeyField(nullable=False) 
    content = StringField(nullable=False)
