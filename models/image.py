from src.model import BaseModel
from src.fields import IntegerField, StringField

class Image(BaseModel):
    id = IntegerField(primary_key=True)
    imageable_id = IntegerField(nullable=False)
    imageable_type = StringField(nullable=False)
    url = StringField(nullable=False)
    # Le relazioni polimorfiche saranno gestite attraverso metodi specifici
