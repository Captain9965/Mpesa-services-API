from src import db
from datetime import datetime
from pytz import timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid

class RequestDump(db.Model):
    uuid_ = db.Column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone("Africa/Nairobi")))
    amount = db.Column(db.Integer, nullable=False, default=0)
    phone = db.Column(db.String(12), nullable=False, default="0")
    shortcode = db.Column(db.String(20), nullable=False, default="0")
    accountReference = db.Column(db.String(50), nullable=False, default="Unknown")
    service = db.Column(db.String(50), nullable=False, default= "MPESA")
    requestStatus = db.Column(db.Boolean, nullable=False, default=False)
    serviceStatus = db.Column(db.Boolean, nullable=False, default=False)
    checkoutRequestId = db.Column(db.String(30), nullable=True)
    merchantRequestId = db.Column(db.String(30), nullable=True)
    mpesaReceiptNumber= db.Column(db.String(30), nullable=True)
    accountBalance= db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.String(50), nullable=True)
    appId = db.Column(db.Integer, nullable=False, default=0)
    errorMessage = db.Column(db.String(100), nullable=False, default= "Okay")

    def __repr__(self):
        return f'<request type : {self.service}, uuid: {self.uuid_}>'
    
    @property
    def serialize(self):
        return {
            "uuid": str(self.uuid_),
            "created at": str(self.created_at),
            "amount": str(self.amount),
            "phone number" : self.phone,
            "short code number" : self.shortcode,
            "Account Reference" : self.accountReference,
            "service request" : self.service,
            "request status" : "success"  if self.requestStatus == True else "Fail",
            "service status" : "success"  if self.serviceStatus == True else "Fail",
            "checkout request ID" : self.checkoutRequestId,
            "merchant request ID" : self.merchantRequestId,
            "Mpesa receipt number" : self.mpesaReceiptNumber,
            "Account Balance" : str(self.accountBalance),
            "updated at" : self.updated_at,
            "application ID" : str(self.appId),
            "Error Message" : self.errorMessage
        }