from pydantic import BaseModel, EmailStr, Field, HttpUrl, constr
from typing import Optional
from enum import Enum
from shared_models import (
    Id,
    Name,
    Address,
    Datetime,
    SubscriptionStatus,
    SubscriptionPlan,
)


class PaymentMethodType(str, Enum):
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    PAYPAL = "PAYPAL"
    BANK_TRANSFER = "BANK_TRANSFER"


class CardBrand(str, Enum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMERICAN_EXPRESS = "AMERICAN_EXPRESS"
    DISCOVER = "DISCOVER"
    JCB = "JCB"


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


class UserType(str, Enum):
    CLIENT = "CLIENT"
    CO_APPLICANT = "CO_APPLICANT"


class User(BaseModel):
    id: Id
    email: EmailStr
    first_name: Name
    last_name: Name
    avatar_url: Optional[HttpUrl] = None
    address: Address
    payment_method: Optional[PaymentMethod] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    subscription_status: Optional[SubscriptionStatus] = None
    user_type: UserType
    created_at: Datetime
    updated_at: Datetime
