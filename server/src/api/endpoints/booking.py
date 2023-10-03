from fastapi import APIRouter, HTTPException, Request, Response
from sqlalchemy import select
from fastapi_async_sqlalchemy import db
from aiogram.utils.web_app import check_webapp_signature, safe_parse_webapp_init_data
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent

from src.bot import bot
from src.config import settings
from src.models import Booking, Venue
from src.schemas.booking import BookingItem, BookingCreate


router = APIRouter()


@router.post("/{venue_id}", status_code=201)
async def book_venue(venue_id: int, request: Request):
    """Book a venue."""
    db_session = db.session

    # Check sent data validity
    json_data = await request.json()
    try:
        web_app_init_data = safe_parse_webapp_init_data(
            token=settings.BOT_TOKEN, init_data=json_data.get("_auth")
        )
    except ValueError:
        return HTTPException(status_code=401, detail="Unauthorized")

    # Check if venue exists
    query = select(Venue).where(Venue.id == venue_id)
    result = await db_session.execute(query)
    venue = result.scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    # Create booking
    user = web_app_init_data.user
    booking = BookingCreate(
        venue_id=venue_id,
        user_id=user.id,
        under_name=json_data.get("under_name"),
        date=json_data.get("date"),
        comment=json_data.get("comment")
    )
    db_obj = Booking(**booking.model_dump())

    db_session.add(db_obj)
    await db_session.commit()
    await db_session.refresh(db_obj)

    # Extract queryId
    query_id = web_app_init_data.query_id

    # Answer web app query
    try:
        await bot.answer_web_app_query(
            web_app_query_id=query_id,
            result=InlineQueryResultArticle(
                type="article",
                id=query_id,
                title="Booking successful!",
                input_message_content=InputTextMessageContent(
                    message_text="Booking successful!"
                )
            )
        )

        return Response(status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
