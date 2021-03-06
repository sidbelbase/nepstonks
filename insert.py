from typing import List

from sqlalchemy.orm import Query

from fetch import latest_stocks
from models import Stock, Telegram, session

StockTable = Query(Stock, session)
TelegramTable = Query(Telegram, session)


def add_stock() -> None:
    scraped_stocks: list = latest_stocks()
    fetched_stocks: int = len(scraped_stocks)
    if fetched_stocks:
        for the_stock in scraped_stocks:
            the_stock_id = StockTable.filter(
                Stock.investment_id == the_stock['investment_id']).first()
            # to avoid inserting the same stock in the table
            if not the_stock_id:
                this_stock = \
                    Stock(
                        company_name=the_stock['company_name'],
                        closing_date=the_stock['closing_date'],
                        investment_id=the_stock['investment_id'],
                        issued_by=the_stock['issued_by'],
                        pdf_url=the_stock['pdf_url'],
                        ratio=the_stock['ratio'],
                        opening_date=the_stock['opening_date'],
                        stock_id=the_stock['stock_id'],
                        scrip=the_stock['scrip'],
                        stock_type=the_stock['stock_type'],
                        units=the_stock['units']
                    )
                session.add(this_stock)
        session.commit()


def add_chat(stock_id: int, message_id: int) -> bool:
    the_stock = StockTable.filter(Stock.id == stock_id).first()
    if the_stock and message_id:
        chat = \
            Telegram(
                stock=the_stock,
                message_id=message_id
            )
        session.add(chat)
        session.commit()
        return True
    return False


def unsent_stocks() -> List[Stock]:
    from datetime import date

    # only send stocks that are newer
    return StockTable.filter(Stock.is_published == False, Stock.opening_date >= date.today()).order_by(Stock.opening_date.desc()).all()


def upcoming_stocks() -> List[Stock]:
    from datetime import date

    # lists all issues that are about to open today
    return StockTable.filter(Stock.opening_date == date.today()).order_by(Stock.opening_date.desc()).all()
