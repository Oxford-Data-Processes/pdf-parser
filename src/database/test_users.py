import pytest
from datetime import datetime
from database.users import (
    PaymentMethodType,
    CardBrand,
    LastFourDigits,
    ExpirationDate,
    PaymentMethod,
    UserType,
    User,
)
from database.shared_models import (
    IdStr,
    NameStr,
    Address,
    DatetimeStr,
    SubscriptionStatus,
    SubscriptionPlan,
    CountryCode,
    dump_json,
)
from pydantic import EmailStr, HttpUrl


def test_create_valid_payment_method():
    payment_method = PaymentMethod(
        type=PaymentMethodType.CREDIT_CARD,
        last_four_digits="1234",
        card_brand=CardBrand.VISA,
        expiration_date="12/25",
        is_default=True,
        billing_address=Address(
            address_line_1="123 Main St",
            address_line_2="Apt 4B",
            city="London",
            state="Greater London",
            postcode="SW1A 1AA",
            country_code=CountryCode.GB,
            country_name="United Kingdom",
        ),
    )
    assert payment_method.type == PaymentMethodType.CREDIT_CARD
    assert payment_method.last_four_digits == "1234"
    assert payment_method.card_brand == CardBrand.VISA
    assert payment_method.expiration_date == "12/25"
    assert payment_method.is_default is True
    assert payment_method.billing_address.city == "London"


def test_create_valid_user():
    user = User(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        email="john.doe@example.com",
        first_name=NameStr("John"),
        last_name=NameStr("Doe"),
        avatar_url=HttpUrl("https://example.com/avatar.jpg"),
        address=Address(
            address_line_1="123 Main St",
            address_line_2="Apt 4B",
            city="London",
            state="Greater London",
            postcode="SW1A 1AA",
            country_code=CountryCode.GB,
            country_name="United Kingdom",
        ),
        payment_method=PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits="1234",
            card_brand=CardBrand.VISA,
            expiration_date="12/25",
            is_default=True,
        ),
        subscription_plan=SubscriptionPlan.PREMIUM,
        subscription_status=SubscriptionStatus.ACTIVE,
        user_type=UserType.CLIENT,
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    dump_json("user_valid", user)
    assert user.email == "john.doe@example.com"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.user_type == UserType.CLIENT
    assert user.subscription_plan == SubscriptionPlan.PREMIUM
    assert user.subscription_status == SubscriptionStatus.ACTIVE


def test_create_valid_co_applicant():
    co_applicant = User(
        id=IdStr("123e4567-e89b-12d3-a456-426614174001"),
        email="jane.doe@example.com",
        first_name=NameStr("Jane"),
        last_name=NameStr("Doe"),
        address=Address(
            address_line_1="123 Main St",
            address_line_2="Apt 4B",
            city="London",
            state="Greater London",
            postcode="SW1A 1AA",
            country_code=CountryCode.GB,
            country_name="United Kingdom",
        ),
        user_type=UserType.CO_APPLICANT,
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    assert co_applicant.email == "jane.doe@example.com"
    assert co_applicant.user_type == UserType.CO_APPLICANT
    assert co_applicant.subscription_plan is None
    assert co_applicant.payment_method is None


def test_invalid_last_four_digits():
    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits="123",  # Too short
            card_brand=CardBrand.VISA,
            expiration_date="12/25",
        )

    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits="12345",  # Too long
            card_brand=CardBrand.VISA,
            expiration_date="12/25",
        )

    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits="abcd",  # Non-numeric
            card_brand=CardBrand.VISA,
            expiration_date="12/25",
        )


def test_invalid_expiration_date():
    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits="1234",
            card_brand=CardBrand.VISA,
            expiration_date="13/25",  # Invalid month
        )

    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits="1234",
            card_brand=CardBrand.VISA,
            expiration_date="00/25",  # Invalid month
        )

    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits="1234",
            card_brand=CardBrand.VISA,
            expiration_date="1225",  # Missing separator
        )


def test_invalid_email():
    with pytest.raises(ValueError):
        User(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            email="invalid-email",  # Invalid email format
            first_name=NameStr("John"),
            last_name=NameStr("Doe"),
            address=Address(
                address_line_1="123 Main St",
                city="London",
                postcode="SW1A 1AA",
                country_code=CountryCode.GB,
                country_name="United Kingdom",
            ),
            user_type=UserType.CLIENT,
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )


def test_invalid_avatar_url():
    with pytest.raises(ValueError):
        User(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            email="john.doe@example.com",
            first_name=NameStr("John"),
            last_name=NameStr("Doe"),
            avatar_url=HttpUrl("invalid-url"),  # Invalid URL format
            address=Address(
                address_line_1="123 Main St",
                city="London",
                postcode="SW1A 1AA",
                country_code=CountryCode.GB,
                country_name="United Kingdom",
            ),
            user_type=UserType.CLIENT,
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )
