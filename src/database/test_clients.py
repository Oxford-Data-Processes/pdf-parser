import pytest
from datetime import datetime
from decimal import Decimal
from .clients import (
    Client,
    EmploymentStatus,
    PhoneCountryCode,
    PhoneNumber,
)
from .shared_models import (
    MonetaryAmount,
    Currency,
    CountryCode,
    CountryName,
    Address,
    AddressLineStr,
    DatetimeStr,
    DateStr,
    CityStr,
    PostcodeStr,
    IdStr,
)


def test_create_valid_client():
    client = Client(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        created_by=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        first_name="Jeff",
        last_name="Marsters",
        email="jeff.marsters@example.com",
        phone_country_code=PhoneCountryCode.GB,
        phone_number=PhoneNumber("7700900123"),
        date_of_birth=DateStr("1990-01-01"),
        address=Address(
            address_line_1=AddressLineStr("123 Main Street"),
            address_line_2=AddressLineStr("Apt 4B"),
            city=CityStr("London"),
            postcode=PostcodeStr("SW1A 1AA"),
            country_name=CountryName.UNITED_KINGDOM,
            country_code=CountryCode.GB,
        ),
        employment_status=EmploymentStatus.EMPLOYED,
        annual_income=MonetaryAmount(amount=32000, currency=Currency.GBP),
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    assert client.first_name == "Jeff"
    assert client.last_name == "Marsters"
    assert client.email == "jeff.marsters@example.com"
    assert client.employment_status == EmploymentStatus.EMPLOYED
    assert isinstance(client.annual_income, MonetaryAmount)
    assert client.annual_income.currency == Currency.GBP
    assert client.annual_income.amount == 32000


def test_create_valid_client_self_employed():
    client = Client(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        created_by=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone_country_code=PhoneCountryCode.GB,
        phone_number=PhoneNumber("7700900456"),
        date_of_birth=DateStr("1985-06-15"),
        address=Address(
            address_line_1=AddressLineStr("456 High Street"),
            city=CityStr("Manchester"),
            postcode=PostcodeStr("M1 1AA"),
            country_name=CountryName.UNITED_KINGDOM,
            country_code=CountryCode.GB,
        ),
        employment_status=EmploymentStatus.SELF_EMPLOYED,
        annual_income=MonetaryAmount(amount=75000, currency=Currency.GBP),
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    assert client.first_name == "Jane"
    assert client.last_name == "Smith"
    assert client.email == "jane.smith@example.com"
    assert client.employment_status == EmploymentStatus.SELF_EMPLOYED
    assert isinstance(client.annual_income, MonetaryAmount)
    assert client.annual_income.currency == Currency.GBP
    assert client.annual_income.amount == 75000


def test_create_valid_client_international():
    client = Client(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        created_by=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        first_name="Hans",
        last_name="Schmidt",
        email="hans.schmidt@example.com",
        phone_country_code=PhoneCountryCode.DE,
        phone_number=PhoneNumber("15123456789"),
        date_of_birth=DateStr("1988-12-31"),
        address=Address(
            address_line_1=AddressLineStr("Hauptstraße 123"),
            city=CityStr("Berlin"),
            postcode=PostcodeStr("10115"),
            country_name=CountryName.GERMANY,
            country_code=CountryCode.DE,
        ),
        employment_status=EmploymentStatus.EMPLOYED,
        annual_income=MonetaryAmount(amount=60000, currency=Currency.EUR),
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    assert client.first_name == "Hans"
    assert client.last_name == "Schmidt"
    assert client.email == "hans.schmidt@example.com"
    assert client.employment_status == EmploymentStatus.EMPLOYED
    assert isinstance(client.annual_income, MonetaryAmount)
    assert client.annual_income.currency == Currency.EUR
    assert client.annual_income.amount == 60000


def test_invalid_phone_number():
    with pytest.raises(ValueError):
        Client(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            created_by=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
            first_name="Test",
            last_name="User",
            email="test.user@example.com",
            phone_country_code=PhoneCountryCode.GB,
            phone_number=PhoneNumber("invalid"),  # Invalid phone number
            date_of_birth=DateStr("1990-01-01"),
            address=Address(
                address_line_1=AddressLineStr("123 Test Street"),
                city=CityStr("London"),
                postcode=PostcodeStr("SW1A 1AA"),
                country_name=CountryName.UNITED_KINGDOM,
                country_code=CountryCode.GB,
            ),
            employment_status=EmploymentStatus.EMPLOYED,
            annual_income=MonetaryAmount(amount=50000, currency=Currency.GBP),
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )


def test_invalid_email():
    with pytest.raises(ValueError):
        Client(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            created_by=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
            first_name="Test",
            last_name="User",
            email="invalid-email",  # Invalid email
            phone_country_code=PhoneCountryCode.GB,
            phone_number=PhoneNumber("7700900123"),
            date_of_birth=DateStr("1990-01-01"),
            address=Address(
                address_line_1=AddressLineStr("123 Test Street"),
                city=CityStr("London"),
                postcode=PostcodeStr("SW1A 1AA"),
                country_name=CountryName.UNITED_KINGDOM,
                country_code=CountryCode.GB,
            ),
            employment_status=EmploymentStatus.EMPLOYED,
            annual_income=MonetaryAmount(amount=50000, currency=Currency.GBP),
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )


def test_invalid_date_format():
    with pytest.raises(ValueError):
        Client(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            created_by=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
            first_name="Test",
            last_name="User",
            email="test.user@example.com",
            phone_country_code=PhoneCountryCode.GB,
            phone_number=PhoneNumber("7700900123"),
            date_of_birth=DateStr("01-01-1990"),  # Invalid date format
            address=Address(
                address_line_1=AddressLineStr("123 Test Street"),
                city=CityStr("London"),
                postcode=PostcodeStr("SW1A 1AA"),
                country_name=CountryName.UNITED_KINGDOM,
                country_code=CountryCode.GB,
            ),
            employment_status=EmploymentStatus.EMPLOYED,
            annual_income=MonetaryAmount(amount=50000, currency=Currency.GBP),
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )
