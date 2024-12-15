from pydantic import BaseModel
from .shared_models import (
    Table,
    DatetimeStr,
    IdStr,
    SubscriptionStatus,
    SubscriptionPlan,
)
from typing import Optional
from typing_extensions import Annotated

from pydantic import Field


StripeCustomerIdStr = Annotated[
    str, Field(pattern=r"^cus_\w{1,30}$", min_length=1, max_length=30)
]

StripeSubscriptionIdStr = Annotated[
    str, Field(pattern=r"^sub_\w{1,30}$", min_length=1, max_length=30)
]


class Subscription(Table):
    user_id: IdStr
    stripe_customer_id: Optional[StripeCustomerIdStr] = None
    stripe_subscription_id: Optional[StripeSubscriptionIdStr] = None
    subscription_plan: SubscriptionPlan
    subscription_status: SubscriptionStatus
    current_period_start: Optional[DatetimeStr] = None
    current_period_end: Optional[DatetimeStr] = None
    cancel_at: Optional[DatetimeStr] = None
    canceled_at: Optional[DatetimeStr] = None
    trial_start: Optional[DatetimeStr] = None
    trial_end: Optional[DatetimeStr] = None
