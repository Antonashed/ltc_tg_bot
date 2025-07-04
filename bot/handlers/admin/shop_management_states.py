import datetime
import os

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import ChatNotFound

from bot.database.methods import (
    check_role,
    select_today_users,
    select_admins,
    get_user_count,
    select_today_orders,
    select_all_orders,
    select_users_balance,
    select_count_items,
    select_count_goods,
    select_count_categories,
    select_count_bought_items,
    check_category,
    create_category,
    delete_category,
    update_category,
    check_subcategory,
    create_subcategory,
    delete_subcategory,
    update_subcategory,
    check_item,
    create_item,
    add_values_to_item,
    update_item,
    delete_item,
    check_value,
    delete_only_items,
    select_bought_item,
)
from bot.database.models import Permission
from bot.handlers.other import get_bot_user_ids
from bot.keyboards import shop_management, goods_management, categories_management, back, item_management, \
    question_buttons, subcategories_management
from bot.logger_mesh import logger
from bot.misc import TgConfig


async def shop_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('⛩️ Меню управления магазином',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=shop_management())
        return
    await call.answer('Недостаточно прав')


async def logs_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    file_path = 'bot.log'
    if role >= Permission.SHOP_MANAGE:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'rb') as document:
                await bot.send_document(chat_id=call.message.chat.id,
                                        document=document)
                return
        else:
            await call.answer(text="❗️ Логов пока нет")
            return
    await call.answer('Недостаточно прав')


async def goods_management_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('⛩️ Меню управления позициями',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=goods_management())
        return
    await call.answer('Недостаточно прав')


async def categories_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('⛩️ Меню управления категориями',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=categories_management())
        return
    await call.answer('Недостаточно прав')


async def add_category_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = 'add_category'
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название категории',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("categories_management"))
        return
    await call.answer('Недостаточно прав')


async def statistics_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        await bot.edit_message_text('Статистика магазина:\n'
                                    '➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                    '<b>◽ПОЛЬЗОВАТЕЛИ</b>\n'
                                    f'◾️Пользователей за 24 часа: {select_today_users(today)}\n'
                                    f'◾️Всего администраторов: {select_admins()}\n'
                                    f'◾️Всего пользователей: {get_user_count()}\n'
                                    '➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                    '◽<b>СРЕДСТВА</b>\n'
                                    f'◾Продаж за 24 часа на: {select_today_orders(today)}$\n'
                                    f'◾Продано товаров на: {select_all_orders()}$\n'
                                    f'◾Пополнений за 24 часа: $\n'
                                    f'◾Средств в системе: {select_users_balance()}$\n'
                                    f'◾Пополнено: $\n'
                                    '➖➖➖➖➖➖➖➖➖➖➖➖➖\n'
                                    '◽<b>ПРОЧЕЕ</b>\n'
                                    f'◾Товаров: {select_count_items()}шт.\n'
                                    f'◾Позиций: {select_count_goods()}шт.\n'
                                    f'◾Категорий: {select_count_categories()}шт.\n'
                                    f'◾Продано товаров: {select_count_bought_items()}шт.',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back('shop_management'),
                                    parse_mode='HTML')
        return
    await call.answer('Недостаточно прав')


async def process_category_for_add(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None
    category = check_category(msg)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if category:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Категория не создана (Такая категория уже существует)',
                                    reply_markup=back('categories_management'))
        return
    create_category(msg)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Категория создана',
                                reply_markup=back('categories_management'))
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'создал новую категорию "{msg}"')


async def delete_category_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = 'delete_category'
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название категории',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("categories_management"))
        return
    await call.answer('Недостаточно прав')


async def process_category_for_delete(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None
    category = check_category(msg)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if not category:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Категория не удалена (Такой категории не существует)',
                                    reply_markup=back('categories_management'))
        return
    delete_category(msg)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Категория удалена',
                                reply_markup=back('categories_management'))
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'удалил категорию "{category["name"]}"')


async def update_category_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'check_category'
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название категории для обновления:',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("categories_management"))
        return
    await call.answer('Недостаточно прав')


async def check_category_for_update(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    category_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    category = check_category(category_name)
    if not category:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Категория не может быть обновлена (Такой категории не существует)',
                                    reply_markup=back('categories_management'))
        return
    TgConfig.STATE[user_id] = 'update_category_name'
    TgConfig.STATE[f'{user_id}_check_category'] = message.text
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Введите новое имя для категории:',
                                reply_markup=back('categories_management'))


async def check_category_name_for_update(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    category = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    old_name = TgConfig.STATE.get(f'{user_id}_check_category')
    TgConfig.STATE[user_id] = None
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    update_category(old_name, category)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text=f'✅ Категория "{category}" обновлена успешно.',
                                reply_markup=back('categories_management'))
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'изменил категорию "{old_name}" на "{category}"')


async def subcategories_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text(
            '⛩️ Меню управления подкатегориями',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=subcategories_management(),
        )
        return
    await call.answer('Недостаточно прав')


async def add_subcategory_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = 'add_subcategory_name'
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text(
            'Введите название подкатегории',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back('subcategories_management'),
        )
        return
    await call.answer('Недостаточно прав')


async def process_subcategory_name(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[user_id] = 'add_subcategory_category'
    TgConfig.STATE[f'{user_id}_subcategory_name'] = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text='Введите категорию для подкатегории:',
        reply_markup=back('subcategories_management'),
    )


async def process_subcategory_category(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    subcat_name = TgConfig.STATE.get(f'{user_id}_subcategory_name')
    category_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if not check_category(category_name):
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text='❌ Подкатегория не создана (Категория не найдена)',
            reply_markup=back('subcategories_management'),
        )
        return
    if check_subcategory(subcat_name):
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text='❌ Подкатегория не создана (Уже существует)',
            reply_markup=back('subcategories_management'),
        )
        return
    create_subcategory(subcat_name, category_name)
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text='✅ Подкатегория создана',
        reply_markup=back('subcategories_management'),
    )
    admin_info = await bot.get_chat(user_id)
    logger.info(
        f"Пользователь {user_id} ({admin_info.first_name}) создал подкатегорию \"{subcat_name}\" в категории \"{category_name}\""
    )


async def delete_subcategory_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = 'delete_subcategory'
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text(
            'Введите название подкатегории',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back('subcategories_management'),
        )
        return
    await call.answer('Недостаточно прав')


async def process_subcategory_for_delete(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    subcat_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if not check_subcategory(subcat_name):
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text='❌ Подкатегория не удалена (Не найдена)',
            reply_markup=back('subcategories_management'),
        )
        return
    delete_subcategory(subcat_name)
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text='✅ Подкатегория удалена',
        reply_markup=back('subcategories_management'),
    )
    admin_info = await bot.get_chat(user_id)
    logger.info(
        f"Пользователь {user_id} ({admin_info.first_name}) удалил подкатегорию \"{subcat_name}\""
    )


async def update_subcategory_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'check_subcategory'
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text(
            'Введите название подкатегории для обновления:',
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=back('subcategories_management'),
        )
        return
    await call.answer('Недостаточно прав')


async def check_subcategory_for_update(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    subcat_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if not check_subcategory(subcat_name):
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message_id,
            text='❌ Подкатегория не может быть обновлена (Не найдена)',
            reply_markup=back('subcategories_management'),
        )
        return
    TgConfig.STATE[user_id] = 'update_subcategory_name'
    TgConfig.STATE[f'{user_id}_old_subcategory'] = subcat_name
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text='Введите новое имя для подкатегории:',
        reply_markup=back('subcategories_management'),
    )


async def check_subcategory_name_for_update(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    new_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    old_name = TgConfig.STATE.get(f'{user_id}_old_subcategory')
    TgConfig.STATE[user_id] = None
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    update_subcategory(old_name, new_name)
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text=f'✅ Подкатегория "{new_name}" обновлена успешно.',
        reply_markup=back('subcategories_management'),
    )
    admin_info = await bot.get_chat(user_id)
    logger.info(
        f"Пользователь {user_id} ({admin_info.first_name}) изменил подкатегорию \"{old_name}\" на \"{new_name}\""
    )


async def goods_settings_menu_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = None
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('⛩️ Выберите действие для позиции',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=item_management())
        return
    await call.answer('Недостаточно прав')


async def add_item_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'create_item_name'
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название позиции',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("item-management"))
        return
    await call.answer('Недостаточно прав')


async def check_item_name_for_add(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    item_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item = check_item(item_name)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    if item:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Позиция не может быть создана (Такая позиция уже существует)',
                                    reply_markup=back('item-management'))
        return
    TgConfig.STATE[user_id] = 'create_item_description'
    TgConfig.STATE[f'{user_id}_name'] = message.text
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Введите описание для позиции:',
                                reply_markup=back('item-management'))


async def add_item_description(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[f'{user_id}_description'] = message.text
    TgConfig.STATE[user_id] = 'create_item_price'
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Введите цену для позиции:',
                                reply_markup=back('item-management'))


async def add_item_price(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if not message.text.isdigit():
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='⚠️ некорректное значение цены.',
                                    reply_markup=back('item-management'))
        return
    TgConfig.STATE[user_id] = 'check_item_subcategory'
    TgConfig.STATE[f'{user_id}_price'] = message.text
    await bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message_id,
        text='Введите подкатегорию, к которой будет относиться товар:',
        reply_markup=back('item-management'),
    )


async def check_subcategory_for_add_item(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    subcategory_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    subcategory = check_subcategory(subcategory_name)
    if not subcategory:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Товар не может быть создан (Подкатегория введена неверно)',
                                    reply_markup=back('item-management'))
        return
    TgConfig.STATE[user_id] = None
    TgConfig.STATE[f'{user_id}_category'] = subcategory['category_name']
    TgConfig.STATE[f'{user_id}_subcategory'] = subcategory['id']
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='У этой позиции будут бесконечные товары? '
                                     '(всем будет высылаться одна копия товара)',
                                reply_markup=question_buttons('infinity', 'item-management'))


async def adding_value_to_position(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    answer = call.data.split('_')[1]
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = 'add_item_value'
    TgConfig.STATE[f'{user_id}_answer'] = answer
    if answer == 'no':
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=message_id,
                                    text='Введите через ; товары для позиции:',
                                    reply_markup=back('item-management'))
    else:
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=message_id,
                                    text='Введите товар для позиции:',
                                    reply_markup=back('item-management'))


async def adding_item(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item_name = TgConfig.STATE.get(f'{user_id}_name')
    item_description = TgConfig.STATE.get(f'{user_id}_description')
    item_price = TgConfig.STATE.get(f'{user_id}_price')
    category_name = TgConfig.STATE.get(f'{user_id}_category')
    subcategory_id = TgConfig.STATE.get(f'{user_id}_subcategory')
    answer = TgConfig.STATE.get(f'{user_id}_answer')
    if answer == 'no':
        values_list = message.text.split(';')
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id)
        create_item(item_name, item_description, item_price, category_name, subcategory_id=subcategory_id)
        for i in values_list:
            add_values_to_item(item_name, i, False)
        group_id = TgConfig.GROUP_ID
        if group_id:
            try:
                await bot.send_message(chat_id=group_id,
                                       text=f'🎁 Залив\n'
                                            f'🏷️ Товар: <b>{item_name}</b>'
                                            f'\n📦 Количество: <b>{len(values_list)}</b>',
                                       parse_mode='HTML')
            except ChatNotFound:
                pass
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='✅ Позиция создана, товар добавлен',
                                    reply_markup=back('item-management'))
        admin_info = await bot.get_chat(user_id)
        logger.info(
            f"Пользователь {user_id} ({admin_info.first_name}) добавил {len(values_list)} значений к товару \"{item_name}\""
        )
    else:
        value = message.text
        await bot.delete_message(chat_id=message.chat.id,
                                 message_id=message.message_id)
        create_item(item_name, item_description, item_price, category_name, subcategory_id=subcategory_id)
        add_values_to_item(item_name, value, True)
        group_id = TgConfig.GROUP_ID if TgConfig.GROUP_ID != -988765433 else None
        if group_id:
            try:
                await bot.send_message(chat_id=group_id,
                                       text=f'🎁 Залив\n'
                                            f'🏷️ Товар: <b>{item_name}</b>'
                                            f'\n📦 Количество: <b>неограниченно</b>',
                                       parse_mode='HTML')
            except ChatNotFound:
                pass
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='✅ Позиция создана, товар добавлен',
                                    reply_markup=back('item-management'))
        admin_info = await bot.get_chat(user_id)
        logger.info(
            f"Пользователь {user_id} ({admin_info.first_name}) добавил неограниченное количество значений к товару \"{item_name}\""
        )


async def update_item_amount_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'update_amount_of_item'
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название позиции',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("item-management"))
        return
    await call.answer('Недостаточно прав')


async def check_item_name_for_amount_upd(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    item_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    item = check_item(item_name)
    if not item:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Товар не может быть добавлен (Такой позиции не существует)',
                                    reply_markup=back('goods_management'))
    else:
        if check_value(item_name) is False:
            TgConfig.STATE[user_id] = 'add_new_amount'
            TgConfig.STATE[f'{user_id}_name'] = message.text
            await bot.edit_message_text(chat_id=message.chat.id,
                                        message_id=message_id,
                                        text='Введите через ; товары для позиции:',
                                        reply_markup=back('goods_management'))
        else:
            await bot.edit_message_text(chat_id=message.chat.id,
                                        message_id=message_id,
                                        text='❌ Товар не может быть добавлен (У данной позиции бесконечный товар)',
                                        reply_markup=back('goods_management'))


async def updating_item_amount(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    values_list = message.text.split(';')
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item_name = TgConfig.STATE.get(f'{user_id}_name')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    for i in values_list:
        add_values_to_item(item_name, i, False)
    group_id = TgConfig.GROUP_ID if TgConfig.GROUP_ID != -988765433 else None
    if group_id:
        try:
            await bot.send_message(chat_id=group_id,
                                   text=f'🎁 Залив\n'
                                        f'🏷️ Товар: <b>{item_name}</b>'
                                        f'\n📦 Количество: <b>{len(values_list)}</b>',
                                   parse_mode='HTML')
        except ChatNotFound:
            pass
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Товар добавлен',
                                reply_markup=back('goods_management'))
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'добавил товары к позиции "{item_name}" в количестве {len(values_list)} шт')


async def update_item_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = 'check_item_name'
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название позиции',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("goods_management"))
        return
    await call.answer('Недостаточно прав')


async def check_item_name_for_update(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    item_name = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    item = check_item(item_name)
    if not item:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Позиция не может быть изменена (Такой позиции не существует)',
                                    reply_markup=back('goods_management'))
        return
    TgConfig.STATE[user_id] = 'update_item_name'
    TgConfig.STATE[f'{user_id}_old_name'] = message.text
    TgConfig.STATE[f'{user_id}_category'] = item['category_name']
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Введите новое имя для позиции:',
                                reply_markup=back('goods_management'))


async def update_item_name(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[f'{user_id}_name'] = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = 'update_item_description'
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Введите описание для позиции:',
                                reply_markup=back('goods_management'))


async def update_item_description(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[f'{user_id}_description'] = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = 'update_item_price'
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='Введите цену для позиции:',
                                reply_markup=back('goods_management'))


async def update_item_price(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if not message.text.isdigit():
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='⚠️ некорректное значение цены.',
                                    reply_markup=back('goods_management'))
        return
    TgConfig.STATE[f'{user_id}_price'] = message.text
    item_old_name = TgConfig.STATE.get(f'{user_id}_old_name')
    if check_value(item_old_name) is False:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='Вы хотите сделать бесконечные товары?',
                                    reply_markup=question_buttons('change_make_infinity', 'goods_management'))
    else:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='Вы хотите отменить бесконечные товары?',
                                    reply_markup=question_buttons('change_deny_infinity', 'goods_management'))


async def update_item_process(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    answer = call.data.split('_')
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item_old_name = TgConfig.STATE.get(f'{user_id}_old_name')
    item_new_name = TgConfig.STATE.get(f'{user_id}_name')
    item_description = TgConfig.STATE.get(f'{user_id}_description')
    category = TgConfig.STATE.get(f'{user_id}_category')
    price = TgConfig.STATE.get(f'{user_id}_price')
    if answer[3] == 'no':
        TgConfig.STATE[user_id] = None
        update_item(item_old_name, item_new_name, item_description, price, category)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    message_id=message_id,
                                    text='✅ Позиция обновлена',
                                    reply_markup=back('goods_management'))
        admin_info = await bot.get_chat(user_id)
        logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                    f'обновил позицию "{item_old_name}" на "{item_new_name}"')
    else:
        if answer[1] == 'make':
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=message_id,
                                        text='Введите товар для позиции:',
                                        reply_markup=back('goods_management'))
            TgConfig.STATE[f'{user_id}_change'] = 'make'
        elif answer[1] == 'deny':
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        message_id=message_id,
                                        text='Введите через ; товары для позиции:',
                                        reply_markup=back('goods_management'))
            TgConfig.STATE[f'{user_id}_change'] = 'deny'
    TgConfig.STATE[user_id] = 'apply_change'


async def update_item_infinity(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    change = TgConfig.STATE[f'{user_id}_change']
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item_old_name = TgConfig.STATE.get(f'{user_id}_old_name')
    item_new_name = TgConfig.STATE.get(f'{user_id}_name')
    item_description = TgConfig.STATE.get(f'{user_id}_description')
    category = TgConfig.STATE.get(f'{user_id}_category')
    price = TgConfig.STATE.get(f'{user_id}_price')
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if change == 'make':
        delete_only_items(item_old_name)
        add_values_to_item(item_old_name, msg, False)
    elif change == 'deny':
        delete_only_items(item_old_name)
        values_list = msg.split(';')
        for i in values_list:
            add_values_to_item(item_old_name, i, False)
    TgConfig.STATE[user_id] = None
    update_item(item_old_name, item_new_name, item_description, price, category)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Позиция обновлена',
                                reply_markup=back('goods_management'))
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'обновил позицию "{item_old_name}" на "{item_new_name}"')


async def delete_item_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    TgConfig.STATE[user_id] = 'process_removing_item'
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите название позиции',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("goods_management"))
        return
    await call.answer('Недостаточно прав')


async def delete_str_item(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    TgConfig.STATE[user_id] = None
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    item = check_item(msg)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if not item:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='❌ Позиция не удалена (Такой позиции не существует)',
                                    reply_markup=back('goods_management'))
        return
    delete_item(msg)
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='✅ Позиция удалена',
                                reply_markup=back('goods_management'))
    admin_info = await bot.get_chat(user_id)
    logger.info(f"Пользователь {user_id} ({admin_info.first_name}) "
                f'удалил позицию "{msg}"')


async def show_bought_item_callback_handler(call: CallbackQuery):
    bot, user_id = await get_bot_user_ids(call)
    TgConfig.STATE[user_id] = 'show_item'
    TgConfig.STATE[f'{user_id}_message_id'] = call.message.message_id
    role = check_role(user_id)
    if role >= Permission.SHOP_MANAGE:
        await bot.edit_message_text('Введите уникальный ID купленного товара',
                                    chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    reply_markup=back("goods_management"))
        return
    await call.answer('Недостаточно прав')


async def process_item_show(message: Message):
    bot, user_id = await get_bot_user_ids(message)
    msg = message.text
    message_id = TgConfig.STATE.get(f'{user_id}_message_id')
    TgConfig.STATE[user_id] = None
    item = select_bought_item(msg)
    await bot.delete_message(chat_id=message.chat.id,
                             message_id=message.message_id)
    if item:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text=f'<b>Товар</b>: <code>{item["item_name"]}</code>\n'
                                         f'<b>Цена</b>: <code>{item["price"]}</code>$\n'
                                         f'<b>Дата покупки</b>: <code>{item["bought_datetime"]}</code>\n'
                                         f'<b>Покупатель</b>: <code>{item["buyer_id"]}</code>\n'
                                         f'<b>Уникальный ID операции</b>: <code>{item["unique_id"]}</code>\n'
                                         f'<b>Значение</b>:\n<code>{item["value"]}</code>',
                                    parse_mode='HTML',
                                    reply_markup=back('show_bought_item'))
        return
    await bot.edit_message_text(chat_id=message.chat.id,
                                message_id=message_id,
                                text='❌ Товар с указанным уникальным ID не найден',
                                reply_markup=back('show_bought_item'))


def register_shop_management(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(statistics_callback_handler,
                                       lambda c: c.data == 'statistics')
    dp.register_callback_query_handler(goods_settings_menu_callback_handler,
                                       lambda c: c.data == 'item-management')
    dp.register_callback_query_handler(add_item_callback_handler,
                                       lambda c: c.data == 'add_item')
    dp.register_callback_query_handler(update_item_amount_callback_handler,
                                       lambda c: c.data == 'update_item_amount')
    dp.register_callback_query_handler(update_item_callback_handler,
                                       lambda c: c.data == 'update_item')
    dp.register_callback_query_handler(delete_item_callback_handler,
                                       lambda c: c.data == 'delete_item')
    dp.register_callback_query_handler(show_bought_item_callback_handler,
                                       lambda c: c.data == 'show_bought_item')
    dp.register_callback_query_handler(shop_callback_handler,
                                       lambda c: c.data == 'shop_management')
    dp.register_callback_query_handler(logs_callback_handler,
                                       lambda c: c.data == 'show_logs')
    dp.register_callback_query_handler(goods_management_callback_handler,
                                       lambda c: c.data == 'goods_management')
    dp.register_callback_query_handler(categories_callback_handler,
                                       lambda c: c.data == 'categories_management')
    dp.register_callback_query_handler(subcategories_callback_handler,
                                       lambda c: c.data == 'subcategories_management')
    dp.register_callback_query_handler(add_subcategory_callback_handler,
                                       lambda c: c.data == 'add_subcategory')
    dp.register_callback_query_handler(delete_subcategory_callback_handler,
                                       lambda c: c.data == 'delete_subcategory')
    dp.register_callback_query_handler(update_subcategory_callback_handler,
                                       lambda c: c.data == 'update_subcategory')
    dp.register_callback_query_handler(add_category_callback_handler,
                                       lambda c: c.data == 'add_category')
    dp.register_callback_query_handler(delete_category_callback_handler,
                                       lambda c: c.data == 'delete_category')
    dp.register_callback_query_handler(update_category_callback_handler,
                                       lambda c: c.data == 'update_category')

    dp.register_message_handler(check_item_name_for_amount_upd,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_amount_of_item')
    dp.register_message_handler(updating_item_amount,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'add_new_amount')
    dp.register_message_handler(check_item_name_for_add,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'create_item_name')
    dp.register_message_handler(add_item_description,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'create_item_description')
    dp.register_message_handler(add_item_price,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'create_item_price')
    dp.register_message_handler(check_subcategory_for_add_item,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'check_item_subcategory')
    dp.register_message_handler(adding_item,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'add_item_value')
    dp.register_message_handler(check_item_name_for_update,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'check_item_name')
    dp.register_message_handler(update_item_name,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_item_name')
    dp.register_message_handler(update_item_description,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_item_description')
    dp.register_message_handler(update_item_price,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_item_price')
    dp.register_message_handler(delete_str_item,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'process_removing_item')
    dp.register_message_handler(process_item_show,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'show_item')
    dp.register_message_handler(process_category_for_add,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'add_category')
    dp.register_message_handler(process_category_for_delete,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'delete_category')
    dp.register_message_handler(check_category_for_update,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'check_category')
    dp.register_message_handler(check_category_name_for_update,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_category_name')
    dp.register_message_handler(process_subcategory_name,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'add_subcategory_name')
    dp.register_message_handler(process_subcategory_category,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'add_subcategory_category')
    dp.register_message_handler(process_subcategory_for_delete,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'delete_subcategory')
    dp.register_message_handler(check_subcategory_for_update,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'check_subcategory')
    dp.register_message_handler(check_subcategory_name_for_update,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'update_subcategory_name')
    dp.register_message_handler(update_item_infinity,
                                lambda c: TgConfig.STATE.get(c.from_user.id) == 'apply_change')

    dp.register_callback_query_handler(adding_value_to_position,
                                       lambda c: c.data.startswith('infinity_'))
    dp.register_callback_query_handler(update_item_process,
                                       lambda c: c.data.startswith('change_'))
