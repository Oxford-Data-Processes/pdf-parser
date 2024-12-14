from pydantic import BaseModel, EmailStr, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from .shared_models import (
    IdStr as Id,
    NameStr as Name,
    DateStr as Date,
    Address,
    DatetimeStr as Datetime,
    MonetaryAmount,
)
from enum import Enum


class PhoneCountryCode(str, Enum):
    GB = "+44"  # United Kingdom
    US = "+1"  # United States
    DE = "+49"  # Germany
    FR = "+33"  # France
    IT = "+39"  # Italy
    ES = "+34"  # Spain
    NL = "+31"  # Netherlands
    BE = "+32"  # Belgium
    IE = "+353"  # Ireland
    DK = "+45"  # Denmark
    SE = "+46"  # Sweden
    NO = "+47"  # Norway
    FI = "+358"  # Finland
    PT = "+351"  # Portugal
    AT = "+43"  # Austria
    CH = "+41"  # Switzerland


class PhoneNumber(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type[str], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.str_schema(
            pattern=r"^\d{1,15}$", min_length=1, max_length=15
        )


class EmploymentStatus(str, Enum):
    EMPLOYED = "EMPLOYED"
    SELF_EMPLOYED = "SELF_EMPLOYED"
    UNEMPLOYED = "UNEMPLOYED"


class Client(BaseModel):
    id: Id
    created_by: Id
    first_name: Name
    last_name: Name
    email: EmailStr
    phone_country_code: PhoneCountryCode
    phone_number: PhoneNumber
    date_of_birth: Date
    address: Address
    employment_status: EmploymentStatus
    annual_income: MonetaryAmount
    created_at: Datetime
    updated_at: Datetime
