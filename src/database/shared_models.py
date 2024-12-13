from pydantic import constr, Field
import pycountry
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class Datetime(constr):
    __root__: str = Field(
        ...,
        description="Datetime in ISO 8601 UTC format.",
        regex=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$",
    )


class Id(constr):
    __root__: str = Field(
        ...,
        regex=r"^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
    )


class Name(constr):
    __root__: str = Field(..., max_length=50)


class Date(constr):
    __root__: str = Field(
        ...,
        regex=r"^(19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$",
    )


class AddressLine(constr):
    __root__: str = Field(..., min_length=1, max_length=100)


class City(constr):
    __root__: str = Field(..., min_length=1, max_length=100)


class Postcode(constr):
    __root__: str = Field(..., regex=r"^[A-Za-z0-9\s\-]+$", min_length=1, max_length=20)


class CountryCode(str, Enum):
    for country in pycountry.countries:
        locals()[country.alpha_2] = country.alpha_2


class CountryName(str, Enum):
    for country in pycountry.countries:
        locals()[country.name] = country.name


class Address(BaseModel):
    address_line_1: AddressLine
    address_line_2: Optional[AddressLine] = None
    city: City
    postcode: Postcode
    country_name: CountryName
    country_code: CountryCode
