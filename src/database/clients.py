from pydantic import BaseModel, EmailStr, constr, Field
from shared_models import Id, Name, Date, Address, Datetime, MonetaryAmount
from enum import Enum

import phonenumbers


class PhoneCountryCode(str, Enum):
    for region in phonenumbers.SUPPORTED_REGIONS:
        code = phonenumbers.region_code_for_number(
            phonenumbers.parse(f"+{phonenumbers.country_code_for_region(region)}")
        )
        locals()[region] = f"+{code}"


class PhoneNumber(constr):
    __root__: str = Field(..., max_length=20)


class EmploymentStatus(str, Enum):
    EMPLOYED = "employed"
    SELF_EMPLOYED = "self_employed"
    UNEMPLOYED = "unemployed"


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
