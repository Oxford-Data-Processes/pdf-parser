from pydantic import BaseModel, Field, constr
import pycountry
from typing import Optional, Annotated
from decimal import Decimal
from enum import Enum


DatetimeStr = Annotated[
    str, Field(pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
]

IdStr = Annotated[
    str,
    Field(
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
    ),
]

NameStr = Annotated[str, Field(max_length=50)]

DateStr = Annotated[
    str, Field(pattern=r"^(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")
]

AddressLineStr = Annotated[str, Field(min_length=1, max_length=100)]

CityStr = Annotated[str, Field(min_length=1, max_length=100)]

PostcodeStr = Annotated[
    str, Field(pattern=r"^[A-Za-z0-9\s\-]+$", min_length=1, max_length=20)
]


class CountryCode(str, Enum):
    GB = "GB"
    US = "US"
    DE = "DE"
    FR = "FR"
    IT = "IT"
    ES = "ES"
    NL = "NL"
    BE = "BE"
    IE = "IE"
    DK = "DK"
    SE = "SE"
    NO = "NO"
    FI = "FI"
    PT = "PT"
    AT = "AT"
    CH = "CH"


class CountryName(str, Enum):
    UNITED_KINGDOM = "United Kingdom"
    UNITED_STATES = "United States"
    GERMANY = "Germany"
    FRANCE = "France"
    ITALY = "Italy"
    SPAIN = "Spain"
    NETHERLANDS = "Netherlands"
    BELGIUM = "Belgium"
    IRELAND = "Ireland"
    DENMARK = "Denmark"
    SWEDEN = "Sweden"
    NORWAY = "Norway"
    FINLAND = "Finland"
    PORTUGAL = "Portugal"
    AUSTRIA = "Austria"
    SWITZERLAND = "Switzerland"


class Address(BaseModel):
    address_line_1: AddressLineStr
    address_line_2: Optional[AddressLineStr] = None
    city: CityStr
    postcode: PostcodeStr
    country_name: CountryName
    country_code: CountryCode


class SubscriptionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    TRIALING = "TRIALING"
    CANCELLED = "CANCELLED"


class SubscriptionPlan(str, Enum):
    BASIC = "BASIC"
    PREMIUM = "PREMIUM"
    ENTERPRISE = "ENTERPRISE"


class Currency(str, Enum):
    USD = "USD"
    GBP = "GBP"
    EUR = "EUR"


class MonetaryAmount(BaseModel):
    """Amount with currency"""

    amount: str
    currency: Currency

    @property
    def decimal_amount(self) -> Decimal:
        return Decimal(self.amount)
