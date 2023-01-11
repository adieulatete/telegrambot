import os
import logging
import re
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext

import db
import keyboards as kb
import expenses
import categories
from exeption import *


# TELEGRAM_API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
TELEGRAM_API_TOKEN = "5766867317:AAGhhuGI1KoiT2BiCOkzmkse3v3fudsybIs"
# Your user ID: 1041994618

# Configure logging
logging.basicConfig(level=logging.INFO, filename="./logging.txt", filemode="w")

storage = MemoryStorage()

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot, storage=storage)


class AddCategoryStatesGroup(StatesGroup):
    """State machine in process adding category"""
    categoryname = State()
    aliases = State()


class EditCategoryStatesGroup(StatesGroup):
    """State machine in process edit category"""
    edit_category = State()
    action = State()
    add_aliases = State()
    remove_aliases = State()
    categoryid = State()
    

@dp.message_handler(commands=["Start"])
async def startup(message: types.Message) -> None:
    """This handler will be called when user sends /Start"""
    user_exists = db.check_user_exists(message.from_user.id)
    if user_exists:
        await message.answer("I'm ready to continue", reply_markup=kb.start_kb())
    else:
        db.add_user(message.from_user.id)
        await message.answer("I'm a telegram finance bot.\nAdd categoris for your expenses", reply_markup=kb.add_category_kb())


@dp.message_handler(lambda message: message.text == "Add category")
async def add_category(message: types.Message) -> None:
    """This handler will be called when user sends 'Add category'"""
    await message.answer("Enter a category name:", reply_markup=kb.cancel_kb())
    await AddCategoryStatesGroup.categoryname.set()


@dp.message_handler(state=AddCategoryStatesGroup.categoryname)
async def set_categoryname(message: types.Message, state: FSMContext) -> None:
    """This handler will be called when user sends category name or 'Cancel'"""
    if message.text == "Cancel":
        await state.finish()
        await message.answer("Continue", reply_markup=kb.start_kb())
        return
    async with state.proxy() as data:
        data["categoryname"] = message.text
    await message.reply("Enter aliases to this category [еда мак фуд]:", reply_markup=kb.cancel_kb())
    await AddCategoryStatesGroup.next()


@dp.message_handler(state=AddCategoryStatesGroup.aliases)
async def set_aliases(message: types.Message, state: FSMContext) -> None:
    """This handler will be called when user sends aliases to category or 'Cancel'"""
    if message.text == "Cancel":
        await state.finish()
        await message.answer("Continue", reply_markup=kb.start_kb())
        return
    try:
        categories._parse_message(message.text)
        async with state.proxy() as data:    
            data["aliases"] = message.text.lower()
            categories.new_category(data['categoryname'], data['aliases'], int(message.from_user.id))
            await message.reply("Your category added!\n"
            f"To add expenses to this category, enter amount and any alias [{message.text}]", reply_markup=kb.start_kb())
            await state.finish()
    except IncorrectMessage as ex:
        await message.answer(str(ex))
        return


@dp.message_handler(lambda message: message.text == "Edit category")
async def edit_category(message: types.Message) -> None:
    """This handler will be called when user sends 'Edit category'"""
    all_categories = categories.get_category(message.from_user.id)
    if not all_categories:
        await message.answer("Categories do not exists", reply_markup=kb.start_kb())
    else:
        await message.answer("Select an action:", reply_markup=kb.select_action_kb())
        await EditCategoryStatesGroup.edit_category.set()


@dp.message_handler(state=EditCategoryStatesGroup.edit_category)
async def edit_category_action(message: types.Message, state: FSMContext) -> None:
    """This handler will be called when user selected action with category"""
    all_categories = categories.get_category(message.from_user.id)
    async with state.proxy() as data:
        if message.text == "Show my categories":
            data["action"] = "show_categories"
            await message.answer("Your categories:", reply_markup=kb.edit_category_ikb(all_categories))
            await EditCategoryStatesGroup.next()
        elif message.text == "Add aliases to category":
            data["action"] = "add_aliases"
            await message.answer("Select category:", reply_markup=kb.edit_category_ikb(all_categories))
            await EditCategoryStatesGroup.next()
        elif message.text == "Remove aliases from category":
            data["action"] = "remove_aliases"
            await message.answer("Select category:", reply_markup=kb.edit_category_ikb(all_categories))
            await EditCategoryStatesGroup.next()
        elif message.text == "Delete category":
            data["action"] = "delete_category"
            await message.answer("Select category:", reply_markup=kb.edit_category_ikb(all_categories))
            await EditCategoryStatesGroup.next()
        elif message.text == "Go back":
            await message.answer("Continue", reply_markup=kb.start_kb())
            await state.finish()


@dp.callback_query_handler(state=EditCategoryStatesGroup.action)
async def edit_category_select(callback: types.CallbackQuery, state) -> None:
    """This handler will be called when user choose category to edit"""
    if callback.data == "Cancel":
        await state.finish()
        await callback.message.answer("Continue", reply_markup=kb.start_kb())
        return
    async with state.proxy() as data:
        if data["action"] == "show_categories":
            await EditCategoryStatesGroup.edit_category.set()
        elif data["action"] == "add_aliases":
            await callback.message.delete()
            await callback.message.answer("Enter new aliases:")
            data["categoryid"] = int(callback.data)
            await EditCategoryStatesGroup.add_aliases.set()
        elif data["action"] == "remove_aliases":
            await callback.message.delete()
            category = categories.get_category(callback.from_user.id, callback.data)
            await callback.message.answer("Choose aliases to be removed:", reply_markup=kb.delete_aliase_ikb(category))
            data["categoryid"] = int(callback.data)
            await EditCategoryStatesGroup.remove_aliases.set()
        elif data["action"] == "delete_category":
            categories.del_category(callback.from_user.id,  int(callback.data))
            await callback.message.delete()
            await callback.message.answer("Category deleted!", reply_markup=kb.start_kb())
            await state.finish()


@dp.message_handler(state=EditCategoryStatesGroup.add_aliases)
async def add_aliases_to_category(message: types.Message, state: FSMContext) -> None:
    """This handler will be called when user choose add aliases to category"""
    try:
        async with state.proxy() as data:
            categories.add_aliases(message.from_user.id, data["categoryid"],message.text)
            await message.answer("New aliases addded!", reply_markup=kb.start_kb())
            await state.finish()
    except IncorrectMessage as ex:
        await message.reply(str(ex))


@dp.callback_query_handler(state=EditCategoryStatesGroup.remove_aliases)
async def remove_aliases_from_category(callback: types.CallbackQuery, state: FSMContext) -> None:
    """This handler will be called when user choose remove aliases from category"""
    try:
        async with state.proxy() as data:  
            categories.remove_aliases(callback.from_user.id, data["categoryid"], callback.data)
            await callback.message.delete()
            await callback.message.answer("Aliases removed!", reply_markup=kb.start_kb())
            await state.finish()
    except IncorrectMessage as ex:
        await callback.message.reply(str(ex))


@dp.message_handler(lambda message: message.text == "Get statistics")
async def get_statistics(message: types.Message) -> None:
    """This handler will be called when user sends 'Get statistics'"""
    await message.answer("Сhoose for what period of time to provide statistics:", reply_markup=kb.statistics_kb())


@dp.message_handler(lambda message: message.text == "Get statistics for the day")
async def get_day_statisctics(message: types.Message) -> None:
    """This handler will be called when user sends 'Get statistics for the day'"""
    day_expense = db.get_statistics(message.from_user.id)
    await message.answer(f"Your expenses this day - {day_expense}р", reply_markup=kb.start_kb())


@dp.message_handler(lambda message: message.text == "Get statistics for the week")
async def get_week_statistics(message: types.Message) -> None:
    """This handler will be called when user sends 'Get statistics for the week'"""
    week_expense = db.get_statistics(message.from_user.id, weeks=1)
    await message.answer(f"Your expenses this week - {week_expense}р", reply_markup=kb.start_kb())


@dp.message_handler(lambda message: message.text == "Get statistics for the month")
async def get_month_statistics(message: types.Message) -> None:
    """This handler will be called when user sends 'Get statistics for the month'"""
    month_expense = db.get_statistics(message.from_user.id, weeks=4)
    await message.answer(f"Your expenses this month - {month_expense}р", reply_markup=kb.start_kb())


@dp.message_handler(lambda message: message.text == "Delete expense")
async def delete_expense_select(message: types.Message) -> None:
    """This handler will be called when user sends 'Delete expense'"""
    all_expenses = expenses.get_expenses(message.from_user.id)
    if all_expenses:
        await message.answer("Your expenses for today:", reply_markup=kb.today_expenses_ikb(all_expenses))
    else:
        await message.answer("No expenses at the moment")


@dp.callback_query_handler(lambda callback: re.match(r"^[\d]+$", str(callback.data)))
async def delete_expense(callback: types.CallbackQuery) -> None:
    """This handler will be called when user selected category to delete'"""
    expenses.delete_expense(callback.from_user.id, int(callback.data))
    await callback.message.delete()
    await callback.message.answer("Expense deleted!")


@dp.message_handler()
async def add_expense(message: types.Message) -> None:
    """This handler will be called when user send message with expense"""
    try:
        categoryname = expenses.add_expense(message.text, message.from_user.id)
        await message.answer(f"Expense added to category - {categoryname}!", reply_markup=kb.start_kb())
    except NoOneExistsCategory as ex:
        await message.answer(str(ex), reply_markup=kb.add_category_kb())
        return
    except IncorrectMessage as ex:
        await message.answer(str(ex), reply_markup=kb.start_kb())
        return


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp, skip_updates=True)
