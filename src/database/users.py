from pydantic import BaseModel, EmailStr, Field, HttpUrl, constr
from typing import Optional
from enum import Enum
from shared_models import Id, Name, Address, Datetime


class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    CANCELED = "canceled"


class PaymentMethodType(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class CardBrand(str, Enum):
    VISA = "visa"
    MASTERCARD = "mastercard"
    AMERICAN_EXPRESS = "american_express"
    DISCOVER = "discover"
    JCB = "jcb"


class LastFourDigits(constr):
    __root__: str = Field(..., regex="^[0-9]{4}$")


class ExpirationDate(constr):
    __root__: str = Field(..., regex="^(0[1-9]|1[0-2])/[0-9]{2}$")


class PaymentMethod(BaseModel):
    type: PaymentMethodType
    last_four_digits: LastFourDigits
    card_brand: CardBrand
    expiration_date: ExpirationDate
    is_default: bool = False
    billing_address: Optional[Address] = None


class User(BaseModel):
    id: Id
    email: EmailStr
    first_name: Name
    last_name: Name
    avatar_url: Optional[HttpUrl] = None
    address: Address
    payment_method: Optional[PaymentMethod] = None
    subscription_tier: Optional[SubscriptionTier] = None
    subscription_status: Optional[SubscriptionStatus] = None
    created_at: Datetime
    updated_at: Datetime
