from pydantic import BaseModel
from shared_models import Id, Datetime
from typing import Optional
from shared_models import SubscriptionStatus, SubscriptionPlan


class Subscription(BaseModel):
    id: Id
    user_id: Id
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
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
