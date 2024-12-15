from pydantic import BaseModel, Field, constr, PositiveInt, confloat, conint, ConfigDict
import pycountry
from typing import Optional, Annotated, Dict, Any
from decimal import Decimal
from enum import Enum
import json
import os

from json import JSONEncoder
from decimal import Decimal
from pydantic import HttpUrl, BaseModel

DatetimeStr = Annotated[
    str, Field(pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
]

IdStr = Annotated[
    str,
    Field(
        pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
    ),
]

NameStr = Annotated[
    str, Field(min_length=1, max_length=50, pattern=r"^[a-zA-Z\s\-']+$")
]

DateStr = Annotated[
    str, Field(pattern=r"^(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$")
]

AddressLineStr = Annotated[
    str,
    Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9\s\-\.,#'ßäöüÄÖÜ]+$",  # Added German characters
    ),
]

CityStr = Annotated[
    str, Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z\s\-']+$")
]

PostcodeStr = Annotated[
    str, Field(pattern=r"^[A-Za-z0-9\s\-]+$", min_length=1, max_length=20)
]

PercentageDecimal = Annotated[Decimal, Field(ge=0, le=1, decimal_places=4)]

AmountDecimal = Annotated[Decimal, Field(ge=0, decimal_places=2)]

PositiveAmount = Annotated[
    PositiveInt, Field(ge=0, le=1_000_000_000_000)  # 1 trillion limit, allowing zero
]

# Integer constraints
NonNegativeInt = Annotated[
    conint(ge=0, le=1_000_000_000_000),  # 1 trillion limit, allowing zero
    Field(description="Amount in smallest currency unit (e.g., cents)"),
]


class Table(BaseModel):
    id: IdStr
    created_at: DatetimeStr
    updated_at: DatetimeStr
    version: conint(ge=1) = Field(default=1)
    is_active: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TransactionCategory(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFERS = "TRANSFERS"
    HEALTHCARE = "HEALTHCARE"
    TRANSPORT = "TRANSPORT"
    FOOD = "FOOD"
    HOUSING = "HOUSING"
    SHOPPING = "SHOPPING"
    MISCELLANEOUS = "MISCELLANEOUS"
    DIGITAL_SERVICES = "DIGITAL_SERVICES"
    ENTERTAINMENT = "ENTERTAINMENT"
    UNCATEGORISED = "UNCATEGORISED"


class TransactionSubcategory(str, Enum):
    # Transfer subcategories
    AUTOMATED_SAVINGS = "AUTOMATED_SAVINGS"
    BANK_TRANSFER = "BANK_TRANSFER"

    # Income subcategories
    SALARY = "SALARY"
    REFUND = "REFUND"
    PERSONAL_TRANSFER = "PERSONAL_TRANSFER"

    # Healthcare subcategories
    FITNESS = "FITNESS"

    # Transport subcategories
    CAR = "CAR"
    PUBLIC = "PUBLIC"
    MICROMOBILITY = "MICROMOBILITY"

    # Food subcategories
    GROCERIES = "GROCERIES"
    TAKEAWAY = "TAKEAWAY"
    DINING_OUT = "DINING_OUT"

    # Housing subcategories
    UTILITIES = "UTILITIES"
    RENT = "RENT"
    MORTGAGE = "MORTGAGE"
    INSURANCE = "INSURANCE"
    MAINTENANCE = "MAINTENANCE"

    # Shopping subcategories
    ONLINE_RETAIL = "ONLINE_RETAIL"
    IN_STORE_RETAIL = "IN_STORE_RETAIL"
    CLOTHING = "CLOTHING"
    ELECTRONICS = "ELECTRONICS"

    # Miscellaneous subcategories
    CASH = "CASH"
    FEES = "FEES"

    # Digital services subcategories
    SUBSCRIPTIONS = "SUBSCRIPTIONS"
    SOFTWARE = "SOFTWARE"
    STREAMING = "STREAMING"

    # Entertainment subcategories
    ACTIVITIES = "ACTIVITIES"
    EVENTS = "EVENTS"
    HOBBIES = "HOBBIES"

    # Personal subcategories
    CARE = "CARE"
    EDUCATION = "EDUCATION"
    GIFTS = "GIFTS"

    OTHER = "OTHER"


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HttpUrl):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, Enum):
            return obj.value  # Convert enum to its value
        return super().default(obj)


def dump_json(name, pydantic_object):
    os.makedirs("jsons", exist_ok=True)  # Create the directory if it doesn't exist
    json_string = json.dumps(
        pydantic_object.model_dump(), cls=CustomJSONEncoder, indent=4
    )
    with open(f"jsons/{name}.json", "w") as f:
        f.write(json_string)


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

    amount: NonNegativeInt
    currency: Currency

    @property
    def decimal_places(self) -> int:
        if self.currency == Currency.GBP:
            return 2
        return 0

    @property
    def decimal_amount(self) -> float:
        return float(self.amount) / 10**self.decimal_places

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"amount": 10000, "currency": "GBP"}]}
    )
