from pydantic import BaseModel
from .shared_models import (
    IdStr as Id,
    DatetimeStr as Datetime,
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


class Subscription(BaseModel):
    id: Id
    user_id: Id
    stripe_customer_id: Optional[StripeCustomerIdStr] = None
    stripe_subscription_id: Optional[StripeSubscriptionIdStr] = None
    subscription_plan: SubscriptionPlan
    subscription_status: SubscriptionStatus
    current_period_start: Optional[Datetime] = None
    current_period_end: Optional[Datetime] = None
    cancel_at: Optional[Datetime] = None
    canceled_at: Optional[Datetime] = None
    trial_start: Optional[Datetime] = None
    trial_end: Optional[Datetime] = None
    created_at: Datetime
    updated_at: Datetime
