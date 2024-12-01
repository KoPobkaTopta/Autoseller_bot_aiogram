from aiogram.types import CallbackQuery
from pymongo import ReturnDocument
from datetime import datetime, timedelta
from tgbot.keyboards.inline import support_keyboard, settings_keyboard
from tgbot.mongo_db.db_api import trial, payments, subs
from tgbot.yoomoneylogic.successful_first_subscription_payment import (
    process_successful_first_subscription_payment,
)
from tgbot.yoomoneylogic.successful_re_subscription_payment import (
    process_successful_re_subscription_payment,
)

# Dictionary mapping subscription amounts to subscription durations in days
SUBSCRIBE_TIMELINE: dict[float, int] = {14.55: 30, 450.0: 90, 900.0: 180}

async def process_check_payment_and_subscription(
    call: CallbackQuery, user_id: int, amount: float
) -> None:
    """
    Processes the payment and subscription for a user after a successful payment.

    Args:
        call (CallbackQuery): The incoming callback query.
        user_id (int): The ID of the user.
        amount (float): The amount of the payment.

    Returns:
        None
    """
    try:
        trials = await trial.find_one(filter={"user_id": user_id})

        trial_flag = trials.get("trial_flag") if trials else None
        if trial_flag == "on":
            await trial.update_one(
                filter={"user_id": user_id},
                update={"$set": {"trial_flag": "Utilized"}},
            )
    except Exception as e:
        print(f"Error updating trial flag: {e}")

    now: datetime = datetime.now()

    await payments.insert_one(
        {
            "user_id": user_id,
            "amount": amount,
            "payment_type": "YooMoney",
            "date": now,
        }
    )

    sub = await subs.find_one(filter={"user_id": user_id, "end_date": {"$gt": now}})
    if sub:
        end_date: datetime = sub["end_date"]
        end_date += timedelta(days=SUBSCRIBE_TIMELINE[amount])

        sub = await subs.find_one_and_update(
            filter={"user_id": user_id, "end_date": {"$gt": now}},
            update={"$set": {"end_date": end_date}},
            return_document=ReturnDocument.AFTER,
        )

        end_date_str: str = sub["end_date"].strftime("%d.%m.%Y")

        await process_successful_re_subscription_payment(
            call, end_date_str, support_keyboard, settings_keyboard
        )
    else:
        await subs.delete_many(filter={"user_id": user_id})
        start_date: datetime = now
        end_date = start_date + timedelta(days=SUBSCRIBE_TIMELINE[amount])

        await subs.insert_one(
            document={
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

        end_date_str: str = end_date.strftime("%d.%m.%Y")

        await process_successful_first_subscription_payment(
            call, end_date_str, support_keyboard, settings_keyboard
        )
