import datetime
import sqlite3


connect = sqlite3.connect("./db/finance.db")
cursor = connect.cursor()
cursor.execute('''PRAGMA foreign_keys=ON''')
connect.commit()


def check_user_exists(userid: int) -> bool:
    """Сhecks if the user is logged in or not"""
    cursor.execute("SELECT * FROM user WHERE userid=:userid", {"userid": userid})
    users = cursor.fetchall()
    if users:
        return True
    return False


def add_user(userid: int) -> None:
    """User registration by userid"""
    cursor.execute("INSERT INTO user(userid) VALUES (?)", (userid,))
    connect.commit()


def get_category(userid: int, categoryid=None) -> list:
    if categoryid:
        cursor.execute("SELECT * FROM category WHERE userid=:userid AND categoryid=:categoryid", {"userid": userid, "categoryid": categoryid})
        result_category = cursor.fetchall()
        return result_category
    cursor.execute("SELECT * FROM category WHERE userid=:userid ORDER BY categoryid", {"userid": userid})
    result_category = cursor.fetchall()
    return result_category


def get_categoryname(userid: int, categoryid: int) -> list:
    cursor.execute("SELECT * FROM category WHERE userid=:userid AND categoryid=:categoryid", {"userid": userid, "categoryid": categoryid})
    result_categoryname = cursor.fetchall()
    return str(result_categoryname[0][1])


def update_aliases_in_category(userid: int, categoryid: int, aliases: int):
    params = (aliases, userid, categoryid)
    cursor.execute("UPDATE category SET aliases=? WHERE userid=? AND categoryid=?", params)
    connect.commit()


def get_statistics(userid: int, weeks: int=0) -> int:
    cursor.execute("SELECT * FROM expense WHERE userid=:userid", {"userid": userid})
    expenses = cursor.fetchall()
    amount = 0.0
    for expense in expenses:
        if datetime.date(int(expense[2][:4]), int(expense[2][5:7]), int(expense[2][8:10])) >= datetime.date.today() - datetime.timedelta(weeks=weeks):
            amount += expense[1]
    return amount


def get_expenses(userid: int) -> list:
    cursor.execute("SELECT * FROM expense WHERE userid=:userid ORDER BY expenseid", {"userid": userid})
    expenses = cursor.fetchall()
    return expenses


def add_category(categoryid: int, categoryname: str, aliases: str, userid: int) -> None:
    params = (categoryid, categoryname, aliases, userid)
    cursor.execute("INSERT INTO category(categoryid, categoryname, aliases, userid) VALUES (?,?,?,?)", params)
    connect.commit()


def add_expense(expenseid: int, amount: int, created: datetime, raw_text: str, categoryid: int, userid: int) -> None:
    params = (expenseid, amount, created, raw_text, categoryid, userid)
    cursor.execute("INSERT INTO expense(expenseid, amount, created, raw_text, categoryid, userid) VALUES (?,?,?,?,?,?)", params)
    connect.commit()


def del_expense(userid: int, expenseid:int) -> None:
    cursor.execute("DELETE FROM expense WHERE userid=:userid AND expenseid=:expenseid", {"userid": userid, "expenseid": expenseid})
    connect.commit()


def del_category(userid: int, categoryid:int) -> None:
    cursor.execute("DELETE FROM category WHERE userid=:userid AND categoryid=:categoryid", {"userid": userid, "categoryid": categoryid})
    connect.commit()


def check_exists_db() -> None:
    cursor.execute("SELECT name FROM sqlite_master \
        WHERE type='table' AND name='expense'")
    table_exists = cursor.fetchall()
    if not table_exists:
        _init_db()


def _init_db() -> None:
    with open("createdb.sql", "r") as file:
        sql = file.read()
    cursor.executescript(sql)
    connect.commit()

check_exists_db()
