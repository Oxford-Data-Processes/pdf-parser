import pytest
from datetime import datetime
from .subscription import (
    Subscription,
)
from .shared_models import (
    IdStr,
    DatetimeStr,
    SubscriptionStatus,
    SubscriptionPlan,
    dump_json,
)


def test_create_valid_subscription():
    subscription = Subscription(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        user_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        stripe_customer_id="cus_123456789",
        stripe_subscription_id="sub_987654321",
        subscription_plan=SubscriptionPlan.PREMIUM,
        subscription_status=SubscriptionStatus.ACTIVE,
        current_period_start=DatetimeStr(datetime.now().isoformat() + "Z"),
        current_period_end=DatetimeStr(
            datetime(2024, 12, 31, 23, 59, 59).isoformat() + "Z"
        ),
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    dump_json("subscriptions_valid", subscription)
    assert subscription.subscription_plan == SubscriptionPlan.PREMIUM
    assert subscription.subscription_status == SubscriptionStatus.ACTIVE
    assert subscription.stripe_customer_id == "cus_123456789"
    assert subscription.stripe_subscription_id == "sub_987654321"


def test_create_valid_trial_subscription():
    trial_start = datetime.now()
    trial_end = datetime(2024, 1, 31, 23, 59, 59)
    subscription = Subscription(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        user_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        subscription_plan=SubscriptionPlan.BASIC,
        subscription_status=SubscriptionStatus.TRIALING,
        trial_start=DatetimeStr(trial_start.isoformat() + "Z"),
        trial_end=DatetimeStr(trial_end.isoformat() + "Z"),
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    dump_json("subscriptions_trial", subscription)
    assert subscription.subscription_plan == SubscriptionPlan.BASIC
    assert subscription.subscription_status == SubscriptionStatus.TRIALING
    assert subscription.trial_start is not None
    assert subscription.trial_end is not None
    assert subscription.stripe_customer_id is None
    assert subscription.stripe_subscription_id is None


def test_create_valid_cancelled_subscription():
    cancelled_at = datetime.now()
    subscription = Subscription(
        id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
        user_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
        stripe_customer_id="cus_123456789",
        stripe_subscription_id="sub_987654321",
        subscription_plan=SubscriptionPlan.ENTERPRISE,
        subscription_status=SubscriptionStatus.CANCELLED,
        current_period_start=DatetimeStr(datetime.now().isoformat() + "Z"),
        current_period_end=DatetimeStr(
            datetime(2024, 12, 31, 23, 59, 59).isoformat() + "Z"
        ),
        cancel_at=DatetimeStr(datetime(2024, 12, 31, 23, 59, 59).isoformat() + "Z"),
        canceled_at=DatetimeStr(cancelled_at.isoformat() + "Z"),
        created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
    )
    dump_json("subscriptions_cancelled", subscription)
    assert subscription.subscription_plan == SubscriptionPlan.ENTERPRISE
    assert subscription.subscription_status == SubscriptionStatus.CANCELLED
    assert subscription.canceled_at is not None
    assert subscription.cancel_at is not None


def test_invalid_subscription_status():
    with pytest.raises(ValueError):
        Subscription(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            user_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
            subscription_plan=SubscriptionPlan.BASIC,
            subscription_status="INVALID_STATUS",  # Invalid status
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )


def test_invalid_subscription_plan():
    with pytest.raises(ValueError):
        Subscription(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            user_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
            subscription_plan="INVALID_PLAN",  # Invalid plan
            subscription_status=SubscriptionStatus.ACTIVE,
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )


def test_invalid_datetime_format():
    with pytest.raises(ValueError):
        Subscription(
            id=IdStr("123e4567-e89b-12d3-a456-426614174000"),
            user_id=IdStr("987fcdeb-51a2-43d7-9012-345678901234"),
            subscription_plan=SubscriptionPlan.BASIC,
            subscription_status=SubscriptionStatus.ACTIVE,
            current_period_start="2023-12-14",  # Invalid datetime format
            created_at=DatetimeStr(datetime.now().isoformat() + "Z"),
            updated_at=DatetimeStr(datetime.now().isoformat() + "Z"),
        )
