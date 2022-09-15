from src import db
from datetime import datetime
from pytz import timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid

class ResponseDump(db.Model):
    uuid_ = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    payload = db.Column(db.JSON(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone("Africa/Nairobi")))
    service = db.Column(db.String(50), nullable=False, default= "MPESA")

    def __repr__(self):
        return f'<response for : {self.service}, uuid: {self.uuid_}>'