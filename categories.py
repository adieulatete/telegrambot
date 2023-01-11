from typing import NamedTuple
import re

import db
from exeption import *


class Category(NamedTuple):
   """Category class"""
   categoryid: int
   categotyname: str
   aliases: list
   userid: int


def new_category(categoryname: str, aliases: str, userid: int) -> None:
   """Add new category by the category name and aliases for users"""
   categories = db.get_category(userid)
   if not categories:
      categoryid = 1
   else:
      for category in categories:
         categoryid = int(category[0]) + 1
   db.add_category(categoryid, categoryname, aliases, int(userid))


def get_category(userid: int, categoryid=None) -> list[Category] | Category:
   """Get all category current user or get specific category by category id"""
   categories = db.get_category(userid, categoryid)
   format_categories = []
   if categoryid is None:
      for category in categories:
         _category = Category(category[0], category[1], category[2], category[3])
         categories.append(_category)
      return format_categories
   return Category(categories[0][0], categories[0][1], str(categories[0][2]).split(sep=" "), categories[0][3])


def _parse_message(raw_message: str) -> None:
   """Checks the aliases introduced by the user for correctness"""
   raw_message += " "
   regex_result = re.match(r'^([а-яА-Яa-zA-Z]+ )+$', raw_message)
   if not regex_result:
      raise IncorrectMessage("Некорректно введенное сообщение. Введите сообщение по схеме: [food фуд еда мак кфс бк]")


def del_category(userid: int, categoryid: int) -> None:
   """Delete category"""
   db.del_category(userid, categoryid)


def add_aliases(userid: int, categoryid: int, raw_message: str) -> None:
   """Add aliases to exists category"""
   _parse_message(raw_message)
   category = db.get_category(userid, categoryid)
   aliases = category[0][2] + " " + raw_message
   db.update_aliases_in_category(userid, categoryid, aliases)


def remove_aliases(userid: int, categoryid: int, alias_for_remove: str) -> None:
   """Remove aliases from exists category"""
   _parse_message(alias_for_remove)
   category = db.get_category(userid, categoryid)
   aliases = str(category[0][2]).replace(alias_for_remove, "")
   db.update_aliases_in_category(userid, categoryid, aliases)


def search_category(alias: str, userid: int) -> int:
   """Searching category by entry alias and return categoryid"""
   categories = db.get_category(userid)
   aliases = {}
   for category in categories:
      aliases[category[0]] = category[2].split(" ")
   for key, value in aliases.items():
      for _alias in value:
         if str(_alias) == str(alias):
            return int(key)
   raise NoOneExistsCategory("No one exists category right now")


def search_categoryname(userid: int, categoryid: int) -> str:
   """Searching category by entry alias and return category name"""
   categoryname = db.get_categoryname(userid, categoryid)
   return categoryname  
