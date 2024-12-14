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
    Name,
    Address,
    Datetime,
    SubscriptionStatus,
    SubscriptionPlan,
    CountryCode,
)
from pydantic import EmailStr, HttpUrl


def test_create_valid_payment_method():
    payment_method = PaymentMethod(
        type=PaymentMethodType.CREDIT_CARD,
        last_four_digits=LastFourDigits("1234"),
        card_brand=CardBrand.VISA,
        expiration_date=ExpirationDate("12/25"),
        is_default=True,
        billing_address=Address(
            line1="123 Main St",
            line2="Apt 4B",
            city="London",
            state="Greater London",
            postal_code="SW1A 1AA",
            country_code=CountryCode.GB,
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
        email=EmailStr("john.doe@example.com"),
        first_name=Name("John"),
        last_name=Name("Doe"),
        avatar_url=HttpUrl("https://example.com/avatar.jpg"),
        address=Address(
            line1="123 Main St",
            line2="Apt 4B",
            city="London",
            state="Greater London",
            postal_code="SW1A 1AA",
            country_code=CountryCode.GB,
        ),
        payment_method=PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits=LastFourDigits("1234"),
            card_brand=CardBrand.VISA,
            expiration_date=ExpirationDate("12/25"),
            is_default=True,
        ),
        subscription_plan=SubscriptionPlan.PREMIUM,
        subscription_status=SubscriptionStatus.ACTIVE,
        user_type=UserType.CLIENT,
        created_at=Datetime(datetime.now().isoformat() + "Z"),
        updated_at=Datetime(datetime.now().isoformat() + "Z"),
    )
    assert user.email == "john.doe@example.com"
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.user_type == UserType.CLIENT
    assert user.subscription_plan == SubscriptionPlan.PREMIUM
    assert user.subscription_status == SubscriptionStatus.ACTIVE


def test_create_valid_co_applicant():
    co_applicant = User(
        id=IdStr("123e4567-e89b-12d3-a456-426614174001"),
        email=EmailStr("jane.doe@example.com"),
        first_name=Name("Jane"),
        last_name=Name("Doe"),
        address=Address(
            line1="123 Main St",
            line2="Apt 4B",
            city="London",
            state="Greater London",
            postal_code="SW1A 1AA",
            country_code=CountryCode.GB,
        ),
        user_type=UserType.CO_APPLICANT,
        created_at=Datetime(datetime.now().isoformat() + "Z"),
        updated_at=Datetime(datetime.now().isoformat() + "Z"),
    )
    assert co_applicant.email == "jane.doe@example.com"
    assert co_applicant.user_type == UserType.CO_APPLICANT
    assert co_applicant.subscription_plan is None
    assert co_applicant.payment_method is None


def test_invalid_last_four_digits():
    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits=LastFourDigits("123"),  # Too short
            card_brand=CardBrand.VISA,
            expiration_date=ExpirationDate("12/25"),
        )

    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits=LastFourDigits("12345"),  # Too long
            card_brand=CardBrand.VISA,
            expiration_date=ExpirationDate("12/25"),
        )

    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits=LastFourDigits("abcd"),  # Non-numeric
            card_brand=CardBrand.VISA,
            expiration_date=ExpirationDate("12/25"),
        )


def test_invalid_expiration_date():
    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits=LastFourDigits("1234"),
            card_brand=CardBrand.VISA,
            expiration_date=ExpirationDate("13/25"),  # Invalid month
        )

    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits=LastFourDigits("1234"),
            card_brand=CardBrand.VISA,
            expiration_date=ExpirationDate("00/25"),  # Invalid month
        )

    with pytest.raises(ValueError):
        PaymentMethod(
            type=PaymentMethodType.CREDIT_CARD,
            last_four_digits=LastFourDigits("1234"),
            card_brand=CardBrand.VISA,
            expiration_date=ExpirationDate("1225"),  # Missing separator
        )


def test_invalid_email():
    with pytest.raises(ValueError):
        User(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            email=EmailStr("invalid-email"),  # Invalid email format
            first_name=Name("John"),
            last_name=Name("Doe"),
            address=Address(
                line1="123 Main St",
                city="London",
                postal_code="SW1A 1AA",
                country_code=CountryCode.GB,
            ),
            user_type=UserType.CLIENT,
            created_at=Datetime(datetime.now().isoformat() + "Z"),
            updated_at=Datetime(datetime.now().isoformat() + "Z"),
        )


def test_invalid_avatar_url():
    with pytest.raises(ValueError):
        User(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            email=EmailStr("john.doe@example.com"),
            first_name=Name("John"),
            last_name=Name("Doe"),
            avatar_url=HttpUrl("invalid-url"),  # Invalid URL format
            address=Address(
                line1="123 Main St",
                city="London",
                postal_code="SW1A 1AA",
                country_code=CountryCode.GB,
            ),
            user_type=UserType.CLIENT,
            created_at=Datetime(datetime.now().isoformat() + "Z"),
            updated_at=Datetime(datetime.now().isoformat() + "Z"),
        )
