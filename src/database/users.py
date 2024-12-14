from pydantic import BaseModel, EmailStr, Field, HttpUrl, constr
from typing import Optional, Annotated
from enum import Enum
from database.shared_models import (
    IdStr,
    NameStr,
    Address,
    DatetimeStr,
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


LastFourDigits = Annotated[str, Field(pattern="^[0-9]{4}$")]
ExpirationDate = Annotated[str, Field(pattern="^(0[1-9]|1[0-2])/[0-9]{2}$")]


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
    id: IdStr
    email: EmailStr
    first_name: NameStr
    last_name: NameStr
    avatar_url: Optional[HttpUrl] = None
    address: Address
    payment_method: Optional[PaymentMethod] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    subscription_status: Optional[SubscriptionStatus] = None
    user_type: UserType
    created_at: DatetimeStr
    updated_at: DatetimeStr
