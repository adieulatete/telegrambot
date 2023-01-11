import re
from typing import NamedTuple
import datetime

from exeption import *
import categories
import db


class Mesage(NamedTuple):
    amount: int
    category: str


class Expense(NamedTuple):
    expenseid: int
    amount: int
    category: str
    created: datetime


def add_expense(raw_message: str, userid: int) -> str:
    expenseid = get_expense_id(userid)
    message = _parse_message(raw_message)
    categoryid = categories.search_category(message.category, userid)
    categoryname = categories.search_categoryname(userid, categoryid)
    db.add_expense(expenseid, message.amount, datetime.datetime.today(), message.category, categoryid, userid)
    return categoryname


def get_expense_id(userid: int) -> int:
    expenses = db.get_expenses(userid)
    if not expenses:
        expenseid = 1
        return expenseid
    else:
        for expense in expenses:
            expenseid = int(expense[0]) + 1
        return expenseid


def get_expenses(userid: int) -> dict:
    raw_expenses = db.get_expenses(userid)
    expenses = [
        _expense for _expense in raw_expenses if datetime.date(int(_expense[2][:4]), int(_expense[2][5:7]), int(_expense[2][8:10])) >= datetime.date.today()]
    list_expenses = []
    for _expense in expenses:
        expenseid = _expense[0]
        amount = _expense[1]
        category = db.get_categoryname(userid, categoryid=_expense[4])
        created = datetime.time(hour=int(_expense[2][11:13]), minute=int(_expense[2][14:16])).strftime("%H:%M")
        list_expenses.append(Expense(expenseid, amount, category, created))
    return list_expenses


def delete_expense(userid: int, expenseid: int) -> None:
    db.del_expense(userid, expenseid)
    

def _parse_message(raw_message):
    regex_result = re.match(r'^([\d]+(\.\d+)?) ([а-яА-Яa-zA-Z]+)$', raw_message)
    if not regex_result or not regex_result.group(0) or not regex_result.group(1) or not regex_result.group(3):
        raise IncorrectMessage("Некорректно введенное сообщение. Введите сообщение по схеме: [20 такси]")
    amount = regex_result.group(1).lower()
    category = regex_result.group(3).lower()
    return Mesage(amount, category)
