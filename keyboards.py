from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

import expenses
import categories


def start_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("Delete expense")],
        [KeyboardButton("Get statistics")],
        [KeyboardButton("Add category")],
        [KeyboardButton("Edit category")]],
        resize_keyboard=True, one_time_keyboard=True)
    return kb


def add_category_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("Add category")],
        ],
        resize_keyboard=True, one_time_keyboard=True)
    return kb


def cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("Cancel")],
        ],
        resize_keyboard=True, one_time_keyboard=True)
    return kb


def select_action_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("Show my categories")],
        [KeyboardButton("Add aliases to category")],
        [KeyboardButton("Remove aliases from category")],
        [KeyboardButton("Delete category")],
        [KeyboardButton("Go back")]],
        resize_keyboard=True, one_time_keyboard=True)
    return kb


def statistics_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton("Get statistics for the day")],
        [KeyboardButton("Get statistics for the week")],
        [KeyboardButton("Get statistics for the month")]],
        resize_keyboard=True, one_time_keyboard=True)
    return kb


def today_expenses_ikb(expenses: list[expenses.Expense]) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for expense in expenses:
        bt = InlineKeyboardButton(f"Date - {expense.created}, category - {expense.category}, amount - {expense.amount}р", 
        callback_data=f"{expense.expenseid}")
        buttons.append(bt)
    ikb.add(*buttons)
    return ikb


def delete_aliase_ikb(category: categories.Category) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for aliase in category.aliases:
        bt = InlineKeyboardButton(f"{aliase}", callback_data=f"{aliase}")
        buttons.append(bt)
    ikb.add(*buttons)
    return ikb


def edit_category_ikb(categories: list[categories.Category]) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for category in categories:
        bt = InlineKeyboardButton(f"Category name - {category.categotyname}, aliases - {category.aliases}", 
        callback_data=f"{category.categoryid}")
        buttons.append(bt)
    bt_cancel = InlineKeyboardButton("Cancel",
        callback_data="Cancel")
    buttons.append(bt_cancel)
    ikb.add(*buttons)
    return ikb
