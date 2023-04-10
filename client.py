from aiogram import types, Dispatcher
from create_bot import dp, bot
from keyboards import kb_client, kb_client_number, buy_menu
from aiogram.types import ReplyKeyboardRemove
from data_base import sqlite_db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton,ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from pyqiwip2p import QiwiP2P

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
import random

key_qiwi = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6Ijgyd3g0Zi0wMCIsInVzZXJfaWQiOiI3OTg1MjA1MjQ0OSIsInNlY3JldCI6Ijc5OWE2MzM4YzE0MjdkZmY1YjhmOTA3NzQwOGM3MDJlODM1MGRlMTE0NGU3MmJjMmJjODQ3NTViNmZjNTdmZmEifX0='

p2p = QiwiP2P(auth_key=key_qiwi)
db = sqlite_db.Database('shop_data.db')

class balance(StatesGroup):
	need_balance = State()
#@dp.message_handler(commands=['Пополнить баланс 💳']) 
async def up_balance(message : types.CallbackQuery):
	callback = message
	await callback.message.delete()
	await bot.send_message(message.from_user.id,'💳 Введите сумму в рублях',reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Главное меню ⬅️')))
	await balance.need_balance.set()
def is_number(_str):
	try:
		int(_str)
		return True
	except ValueError:
		return False

async def balance_uper(message: types.Message, state: FSMContext):
	if message.text!="Главное меню ⬅️":
		if message.chat.type == 'private':
			if is_number(message.text):
				if int(message.text)>=15:
					global message_money
					message_money = int(message.text)
					comment = str(message.from_user.id)+"_"+str(random.randint(1000,9999))
					bill = p2p.bill(amount = message_money,lifetime=15,comment=comment)


					db.add_check(message.from_user.id,message_money,bill.bill_id)

					await bot.send_message(message.from_user.id,f"Вам нужно отправить {message_money} руб. на наш счет киви\nСсылку: {bill.pay_url}\nУказав комментарий к оплате: {comment}",reply_markup=buy_menu(url=bill.pay_url,bill=bill.bill_id))
					await state.finish()
				else:
					await bot.send_message(message.from_user.id,"Минимальная сумма 15 руб.")
			else:
				await bot.send_message(message.from_user.id,"Введите целое число")
			
	else:
		await state.finish()
		await bot.send_message(message.from_user.id,'Главное меню ⬅️',reply_markup=kb_client)


async def check(callback: types.CallbackQuery):
	global message_money
	bill = str(callback.data[6:])
	info = db.get_check(bill)
	if info != False:
		if str(p2p.check(bill_id=bill).status) =="PAID":
			user_money = db.user_money(callback.from_user.id)

			money = int(info[2])
			db.set_money(callback.from_user.id, user_money+money)
			await bot.send_message(callback.from_user.id,f"Успешная оплата!\nБаланс пополнен на {message_money} руб.")
			db.delete_check(bill)
		else:
			await bot.send_message(callback.from_user.id,"Ваша транзакция не найдена!\nЕсли у вас возникла ошибка, обратитесь в поддержку",reply_markup=buy_menu(False,bill=bill))
	else:
		await bot.send_message(callback.from_user.id,"Счет не найден")


Name_bay = None
#@dp.message_handler(commands=['start','help'])
async def commands_start(message : types.Message):
	if db.user_exists(message.from_user.id) == False:
		db.add_user(message.from_user.id)
	try:
		await bot.send_message(message.from_user.id,"Что вас интересует?", reply_markup=kb_client)
		await message.delete()
	except:
		await message.reply("Общение с ботом через лс, пиши ему")

async def mein_menu(message: types.Message):
	await bot.send_message(message.from_user.id,"Главное меню ⬅️", reply_markup=kb_client)
#@dp.message_handler(commands=['Тех.помощ'])
async def pizza_open_command(message : types.Message):
	await bot.send_message(message.from_user.id,'Хотите связаться с тех.поддержкой?',reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton('Связаться',callback_data = 'tech_help_')))

#@dp.message_handler(commands=['Расположение'])
async def pizza_place_command(message : types.Message):
	await bot.send_message(message.from_user.id,"Наши отзывы: @Re_zxShaSty")

#@dp.message_handler(commands=['GJREGFDNM'])тут покупка
async def pokupka(message : types.Message):
	await bot.send_message(-1001547431503,"@" + message.from_user.username + ": " + message.text[6:])

class Number(StatesGroup):
	Number_user = State()
class Number_akk(StatesGroup):
	Number_user = State()
class usl_akk_data(StatesGroup):
	log = State()
	#pas = State()

#@dp.callback_bay_handler(lambda x: x.data and x.data.startswith('del ')) кнопка покупки
async def del_bays_uls_run(bay: types.CallbackQuery):
	global bay_data
	bay_data = bay
	await usl_akk_data.log.set()
	await bot.send_message(bay.from_user.id,'Нам нужны данные от вашего акканута что бы оказать услугу, введите логин\nЕсли поймете что ввели что то не так, нажмите главное меню и начните сначала',reply_markup = ReplyKeyboardMarkup().add(KeyboardButton('Главное меню ⬅️')))

async def save_log_usl(message:types.Message,state: FSMContext):
	if message.text != 'Главное меню ⬅️':
		global log_usl
		log_usl = message.text
		await state.finish()
		await bot.send_message(message.from_user.id,f'Логин: {log_usl}\nЕсли все верно нажмите подтвердить',reply_markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text = "Подвердить",callback_data =f'$')))
	else:
		await bot.send_message(message.from_user.id,'Главное меню ⬅️',reply_markup=kb_client)
		await state.finish()






#	if message.text != 'Главное меню ⬅️':
#		global log_usl
#		log_usl = message.text
#		await bot.send_message(message.from_user.id,'Теперь введите пароль от вашего аккаунта')
#		await usl_akk_data.next()
#	else:
#		await bot.send_message(message.from_user.id,'Главное меню ⬅️',reply_markup=kb_client)
#		await state.finish()

#async def save_pass_usl(message:types.Message,state: FSMContext):
#	if message.text != 'Главное меню ⬅️':
#		global pass_usl
#		pass_usl = message.text
#		await state.finish()
#		await bot.send_message(message.from_user.id,f'Логин: {log_usl}\nПароль: {pass_usl}\nЕсли все верно нажмите подтвердить',reply_markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text = "Подвердить",callback_data =f'$')))
#	else:
#		await bot.send_message(message.from_user.id,'Главное меню ⬅️',reply_markup=kb_client)
#		await state.finish()

async def del_bays_uls_run_dollar(bay: types.CallbackQuery):
	global Name_bay
	bay=bay_data 
	Name = ((bay['data']).strip('$Send_bay_usl')).split(',')
	Name_b = Name[0][3:-1]
	price = int(Name[1][2:-2])
	Name_bay = Name_b
	user_money = db.user_money(bay.from_user.id)
	if user_money >= price:
			if bay.from_user.username is not None:
				db.set_money(bay.from_user.id,user_money-price)
				await bay.message.answer('Ваш заказ' +(' "')+Name_bay+('" ') +'передан '+(f'администратору, ожмдайте выполненя услуги'))
				await bot.send_message(-1001547431503,"@" + str(bay.from_user.username) +  " купил:"+Name_bay+f'\nВот данные его аккаунта\nЛогин:{log_usl}')						
			else:
				await bay.message.answer('Что бы сделать заказ мне нужен твой номер телефона.Введи его что бы мы могли с тобой связаться)')
				await Number_akk.Number_user.set()
	else:
		await bay.message.answer('На вашем счете недостаточно средств, пополните счет')




#для номера
#async def load_Number(message : types.Message):
	#await Number.Number_user.set()
	#await bot.send_message(message.from_user.id,'Что бы сделать заказ мне нужен твой номер телефона.Введи его что бы\
	# мы могли с тобой связаться', reply_markup=kb_client_number)
	

#сохр номера
#@dp.message_handler(state=FSMAdmin.name)
async def Save_number_usl(bay: types.Message, state: FSMContext):
		global Name_bay
		message = bay
		Name_bay = Name_bay
		if len(str(message))<258:
			await message.reply('это не может быть номером, поверьте, не ошиблись ли вы')

		else:
			async with state.proxy() as data:
				data['Number_user'] = message.text
			await message.answer('Ваш заказ' +(' "')+Name_bay+('" ') +'передан '+(f'администратору, ожмдайте выполненя услуги'))
			await bot.send_message(-1001547431503,"@" + str(bay.from_user.username) +  " купил:"+Name_bay+f'\nВот данные его аккаунта\nЛогин:{log_usl}')
			await state.finish()








async def del_bays_akk_run(bay: types.CallbackQuery):
	global Name_bay
	Name = ((bay['data']).strip('Send_bay')).split(',')
	Name_b = Name[0][3:-1]
	price = int(Name[1][2:-2])
	Name_bay = Name_b
	global pas
	global log
	log = passwords.get(Name_bay)[0]
	pas = passwords.get(Name_bay)[1]
	user_money = db.user_money(bay.from_user.id)
	if user_money >= price:
		if bay.from_user.username is not None:
			db.set_money(bay.from_user.id,user_money-price)
			await bay.message.answer('Ваш заказ' +(' "')+Name_bay+('" ') +'передан '+(f'администратору, скоро он с вами свяжется,а пока вот данные от вашего аккаунта:\nЛогин: {log}\nПароль: {pas}'))	
			await bot.send_message(-1001547431503,"@" + str(bay.from_user.username) +  " хочет купить:"+Name_bay)
			if ('Tanks' in Name_bay) or ('wot' in Name_bay):
				sqlite_db.sql_delete_akk_wot(Name_bay)
			if 'Brawl' in Name_bay:
				sqlite_db.sql_delete_akk_brawl(Name_bay)
			if 'PUBG' in Name_bay:
				sqlite_db.sql_delete_akk_PUBG(Name_bay)
			if 'standoff' in Name_bay:
				sqlite_db.sql_delete_akk_standoff(Name_bay)				
		else:
			await bay.message.answer('Что бы сделать заказ мне нужен твой номер телефона.Введи его что бы мы могли с тобой связаться)')
			await Number.Number_user.set()
	else:
		await bay.message.answer('На вашем счете недостаточно средств, пополните счет')
class help_number(StatesGroup):
	nomer = State()
async def tech_help(callback:types.CallbackQuery):
	if callback.from_user.username is not None:
		await bot.send_message(-1001547431503,"@" + str(callback.from_user.username) +  " хочет обратится в поддержку")
	else:
		await callback.message.answer('Что бы оставить запрос в тех.поддержку мне нужен твой номер телефона.Введи его что бы мы могли с тобой связаться)')
		await help_number.nomer.set()

async def Save_number_help(message: types.Message, state: FSMContext):
	if len(str(message))<258:
		await message.reply('это не может быть номером, поверьте, не ошиблись ли вы')	
	else:
		async with state.proxy() as data:
			data['Number_user'] = message.text
		await state.finish()
		await bot.send_message(-1001547431503,"Клиент с номером " + str(message.text) +  " хочет обратится в поддержку")
async def Save_number(message: types.Message, state: FSMContext):
		global Name_bay
		Name_bay = Name_bay
		if len(str(message))<258:
			await message.reply('это не может быть номером, поверьте, не ошиблись ли вы')
		else:
			async with state.proxy() as data:
				data['Number_user'] = message.text
			await state.finish()
			await message.reply(f'администратору, скоро он с вами свяжется,а пока вот данные от вашего аккаунта:\nЛогин: {log_usl}')
			await bot.send_message(-1001547431503,"Клиент с номером " + str(message.text) +  " хочет купить:"+Name_bay)
			if ('Tanks' in Name_bay) or ('wot' in Name_bay):
				sqlite_db.sql_delete_akk_wot(Name_bay)
			if 'Brawl' in Name_bay:
				sqlite_db.sql_delete_akk_brawl(Name_bay)
			if 'PUBG' in Name_bay:
				sqlite_db.sql_delete_akk_PUBG(Name_bay)
			if 'standoff' in Name_bay:
				sqlite_db.sql_delete_akk_standoff(Name_bay)	







async def get_click(message:types.Message):
	await bot.send_message(message.from_user.id,'+1',reply_markup = ReplyKeyboardMarkup(resize_keyboard = True).add(KeyboardButton('Заработать')).add(KeyboardButton('Еще какая нибудь кнопка')))



#Показать товары
async def show_types_shop(message : types.Message):
	kb_show = InlineKeyboardMarkup().add(InlineKeyboardButton("Аккаунты",callback_data = 'show_akk_shop_'))\
		.add(InlineKeyboardButton("Услуги",callback_data = 'show_uslugi_shop_'))
	await bot.send_message(message.from_user.id,'Выберете категорию товаров:',reply_markup =kb_show )

async def show_akk_shop(callback:types.CallbackQuery):
	await callback.message.delete()
	kb_show = InlineKeyboardMarkup().add(InlineKeyboardButton("World Of Tanks Blitz",callback_data = 'akk_WOT_Blitz_'))\
		.add(InlineKeyboardButton("Brawl Stars",callback_data = 'akk_Brawl_stars_'))\
		.add(InlineKeyboardButton("PUBG Mobile",callback_data = 'akk_PUBG_M_'))\
		.add(InlineKeyboardButton("Standoff 2",callback_data = 'akk_Standoff_'))\
		.add(InlineKeyboardButton("Назад",callback_data = 'back_to_shop_'))
	await bot.send_message(callback.from_user.id,'Выберете категорию аккаунтов:',reply_markup =kb_show )	


async def show_uslugi_shop(callback:types.CallbackQuery):
	await callback.message.delete()
	kb_show = InlineKeyboardMarkup().add(InlineKeyboardButton("World Of Tanks Blitz",callback_data = 'usl_WOT_Blitz_'))\
		.add(InlineKeyboardButton("Brawl Stars",callback_data = 'usl_Brawl_stars_'))\
		.add(InlineKeyboardButton("PUBG Mobile",callback_data = 'usl_PUBG_M_'))\
		.add(InlineKeyboardButton("Standoff 2",callback_data = 'usl_Standoff_'))\
		.add(InlineKeyboardButton("Назад",callback_data = 'back_to_shop_'))
	await bot.send_message(callback.from_user.id,'Выберете категорию услуг:',reply_markup =kb_show )	

async def back_to_shop(callback : types.CallbackQuery):
	await callback.message.delete()
	await show_types_shop((callback))
#Показать список разных акков
async def akk_WOT_Blitz(message:types.CallbackQuery):
	callback = message
	await callback.message.delete()
	read = await sqlite_db.sql_read_akk_wot()
	global passwords
	passwords = {} 
	for ret in read:
		passwords.update({ret[1]:(ret[4],ret[5])})
		await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание:{ret[2]}\nЦена {ret[3]}',reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Купить {ret[1]}', callback_data=f'Send_bay {ret[1],ret[3]}')),disable_notification=True)
		#await bot.send_message(message.from_user.id, text='^^^', reply_markup=InlineKeyboardMarkup().\
		#	add(InlineKeyboardButton(f'Купить {ret[1]}', callback_data=f'Send_bay {ret[1]}')),disable_notification=True)
	await bot.send_message(message.from_user.id,'Вот список наших таваров, что бы купить нажмите кнопку под нужным товаром')	

async def akk_Brawl_stars(message:types.CallbackQuery):
	callback = message
	await callback.message.delete()
	read = await sqlite_db.sql_read_akk_brawl()
	global passwords
	passwords = {} 
	for ret in read:
		passwords.update({ret[1]:(ret[4],ret[5])})
		await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание:{ret[2]}\nЦена {ret[3]}',reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Купить {ret[1]}', callback_data=f'Send_bay {ret[1],ret[3]}')),disable_notification=True)
	await bot.send_message(message.from_user.id,'Вот список наших таваров, что бы купить нажмите кнопку под нужным товаром')

async def akk_PUBG_M(message:types.CallbackQuery):
	callback = message
	await callback.message.delete()
	read = await sqlite_db.sql_read_akk_PUBG()
	global passwords
	passwords = {} 
	for ret in read:
		passwords.update({ret[1]:(ret[4],ret[5])})
		await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание:{ret[2]}\nЦена {ret[3]}',reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Купить {ret[1]}', callback_data=f'Send_bay {ret[1],ret[3]}')),disable_notification=True)
	await bot.send_message(message.from_user.id,'Вот список наших таваров, что бы купить нажмите кнопку под нужным товаром')

async def akk_Standoff(message:types.CallbackQuery):
	callback = message
	await callback.message.delete()
	read = await sqlite_db.sql_read_akk_standoff()
	global passwords
	passwords = {} 
	for ret in read:
		passwords.update({ret[1]:(ret[4],ret[5])})
		await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание:{ret[2]}\nЦена {ret[3]}',reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Купить {ret[1]}', callback_data=f'Send_bay {ret[1],ret[3]}')),disable_notification=True)
	await bot.send_message(message.from_user.id,'Вот список наших таваров, что бы купить нажмите кнопку под нужным товаром')


async def usl_WOT_Blitz(message:types.CallbackQuery):
	callback = message
	await callback.message.delete()
	read = await sqlite_db.sql_read_usl_wot()
	for ret in read:
		await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание:{ret[2]}\nЦена {ret[3]}',reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Купить {ret[1]}', callback_data=f'Send_bay_usl {ret[1],ret[3]}')),disable_notification=True)
	await bot.send_message(message.from_user.id,'Вот список наших таваров, что бы купить нажмите кнопку под нужным товаром')	

async def usl_Brawl_stars(message:types.CallbackQuery):
	callback = message
	await callback.message.delete()
	read = await sqlite_db.sql_read_usl_brawl()
	for ret in read:
		await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание:{ret[2]}\nЦена {ret[3]}',reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Купить {ret[1]}', callback_data=f'Send_bay_usl {ret[1],ret[3]}')),disable_notification=True)
	await bot.send_message(message.from_user.id,'Вот список наших таваров, что бы купить нажмите кнопку под нужным товаром')	

async def usl_PUBG(message:types.CallbackQuery):
	callback = message
	await callback.message.delete()
	read = await sqlite_db.sql_read_usl_PUBG()
	for ret in read:
		await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание:{ret[2]}\nЦена {ret[3]}',reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Купить {ret[1]}', callback_data=f'Send_bay_usl {ret[1],ret[3]}')),disable_notification=True)
	await bot.send_message(message.from_user.id,'Вот список наших таваров, что бы купить нажмите кнопку под нужным товаром')

async def usl_Standoff(message:types.CallbackQuery):
	callback = message
	await callback.message.delete()
	read = await sqlite_db.sql_read_usl_standoff()
	for ret in read:
		await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание:{ret[2]}\nЦена {ret[3]}',reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Купить {ret[1]}', callback_data=f'Send_bay_usl {ret[1],ret[3]}')),disable_notification=True)
	await bot.send_message(message.from_user.id,'Вот список наших таваров, что бы купить нажмите кнопку под нужным товаром')

#@dp.message_handler(commands=['Товары'])
async def pizza_menu_command(message : types.CallbackQuery):

	#await sqlite_db.sql_read(message)
	read = await sqlite_db.sql_read2()
	for ret in read:
		await bot.send_photo(message.from_user.id, ret[0], f'{ret[1]}\nОписание:{ret[2]}\nЦена {ret[-1]}',disable_notification=True)
		await bot.send_message(message.from_user.id, text='^^^', reply_markup=InlineKeyboardMarkup().\
			add(InlineKeyboardButton(f'Купить {ret[1]}', callback_data=f'Send_bay {ret[1]}')),disable_notification=True)
	await bot.send_message(message.from_user.id,'Вот список наших таваров, что бы купить нажмите кнопку под нужным товаром')



async def my_balance(message:types.Message):
	user_money = db.user_money(message.from_user.id)
	await bot.send_message(message.from_user.id,f'💸Баланс: {user_money} р.',reply_markup = InlineKeyboardMarkup().add(InlineKeyboardButton('Пополнить баланс 💳',callback_data = 'Пополнить баланс 💳_')))

def register_handlers_client(dp : Dispatcher):
	dp.register_message_handler(get_click, Text(equals='Заработать'))

	dp.register_message_handler(mein_menu, Text(equals='Главное меню ⬅️'))
	dp.register_message_handler(commands_start,commands=['start','help'])
	dp.register_message_handler(pizza_open_command, Text(equals='Тех.поддержка 👤'))
	dp.register_message_handler(pizza_place_command, Text(equals='Отзывы 👥'))
	dp.register_message_handler(show_types_shop, Text(equals='Товары 📦'))
	
	dp.register_callback_query_handler(del_bays_akk_run,lambda x: x.data and x.data.startswith('Send_bay '))
	dp.register_callback_query_handler(del_bays_uls_run,lambda x: x.data and x.data.startswith('Send_bay_usl '))
	dp.register_callback_query_handler(del_bays_uls_run_dollar,lambda x: x.data and x.data.startswith('$'))
	dp.register_message_handler(pokupka, commands=['Send'])
	#dp.register_message_handler(load_Number,state=None)
	dp.register_message_handler(save_log_usl,state=usl_akk_data.log)
	#dp.register_message_handler(save_pass_usl,state=usl_akk_data.pas)
	dp.register_message_handler(Save_number,state=Number_akk.Number_user)
	dp.register_message_handler(Save_number_help,state=help_number.nomer)
	dp.register_message_handler(Save_number_usl,state=Number.Number_user)


	dp.register_callback_query_handler(pizza_menu_command,text = 'show_akk_shop__')
	dp.register_callback_query_handler(show_akk_shop,text = 'show_akk_shop_')
	dp.register_callback_query_handler(show_uslugi_shop,text = 'show_uslugi_shop_')

	dp.register_callback_query_handler(back_to_shop,text = 'back_to_shop_')
	dp.register_message_handler(my_balance, Text(equals='Баланс 💸'))
	dp.register_callback_query_handler(check,text_contains="cheсk_")
	dp.register_message_handler(balance_uper,state=balance.need_balance)
	dp.register_callback_query_handler(up_balance, text_contains='Пополнить баланс 💳_')

	dp.register_callback_query_handler(akk_WOT_Blitz,text_contains="akk_WOT_Blitz_")
	dp.register_callback_query_handler(akk_Brawl_stars,text_contains="akk_Brawl_stars_")
	dp.register_callback_query_handler(akk_PUBG_M,text_contains="akk_PUBG_M_")
	dp.register_callback_query_handler(akk_Standoff,text_contains="akk_Standoff_")

	dp.register_callback_query_handler(tech_help,text_contains="tech_help_")

	dp.register_callback_query_handler(usl_WOT_Blitz,text_contains="usl_WOT_Blitz_")
	dp.register_callback_query_handler(usl_Brawl_stars,text_contains="usl_Brawl_stars_")
	dp.register_callback_query_handler(usl_PUBG,text_contains="usl_PUBG_M_")
	dp.register_callback_query_handler(usl_Standoff,text_contains="usl_Standoff_")