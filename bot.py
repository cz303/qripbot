import telebot, Settings, re, string, random, sqlite3, threading, Queue, time, StringIO, requests
from captcha.image import ImageCaptcha
from telebot import types

bot = telebot.TeleBot(Settings.BOT_TOKEN)
users_data = {}
db_write_queue = Queue.Queue()

yes_no_keyboard = types.ReplyKeyboardMarkup()
yes_no_keyboard.row(types.KeyboardButton("< Yes >"))
yes_no_keyboard.row(types.KeyboardButton("< No >"))

cancel_keyboard = types.ReplyKeyboardMarkup()
cancel_keyboard.row(types.KeyboardButton("< Cancel >"))

start_markup =types.ReplyKeyboardMarkup()
start_markup.row(types.KeyboardButton("< Signup >"))
start_markup.row(types.KeyboardButton("< Balance >"))

# Thread to manage db insertions / updates since sqlite doesnt like concurrency
def db_connector():
	global q
	db = sqlite3.connect("users.db")
	c = db.cursor()
	try:
		c.execute("""
			CREATE TABLE USERS (user_id integer, points integer, email text, twitter text, erc20 text, referer integer)
		""")
	except:
		pass
	while 1:
		if not db_write_queue.empty():
			query = db_write_queue.get()
			c.execute(query[0], query[1])
			db.commit()
		time.sleep(0.001)

def init_user(user_id, referer=''):
	global users_data
	try:
		users_data[user_id]
	except:
		users_data[user_id] = {}
		users_data[user_id]['step'] = 0
		users_data[user_id]['email'] = ''
		users_data[user_id]['erc20'] = ''
		users_data[user_id]['twitter'] = ''
		users_data[user_id]['captcha'] = ''
		users_data[user_id]['referer'] = referer

@bot.message_handler(commands=['start'])
def do(message):

	# Check if user is registered, if not store referer ID
	try:
		ref_id = message.text.split(" ")[1]
		int(ref_id)
	except:
		ref_id = None
	init_user(message.from_user.id, ref_id)

	bot.reply_to(message, Settings.START_MESSAGE, parse_mode='HTML', reply_markup=start_markup)

@bot.message_handler(commands=['export'])
def do(message):
	if message.chat.id != Settings.ADMIN_ID:
		return
		
	db = sqlite3.connect("users.db")
	c = db.cursor() # Only for read operations

	# Fetch data
	c.execute("SELECT * FROM USERS")
	users = c.fetchall()

	# Build CSV file
	csv = "User ID;Points;E-Mail;Twitter;ERC20;Referer\n" + "\n".join(
		";".join(str(b) for b in a) for a in users
	)
	temp = StringIO.StringIO()
	temp.write(csv)
	temp.seek(0,0)
	requests.post("https://api.telegram.org/bot%s/sendDocument" % Settings.BOT_TOKEN, params={
			'chat_id': message.chat.id
		}, files={
			'document': ('export.csv', temp)
		})
	temp.close()

@bot.message_handler(func=lambda message: message.text == "< Balance >")
def do(message):
	db = sqlite3.connect("users.db")
	c = db.cursor() # Only for read operations
	c.execute("SELECT points FROM USERS WHERE user_id = ?", (str(message.from_user.id),))
	balance = c.fetchone()
	if balance:
		bot.reply_to(message, Settings.BALANCE_MESSAGE % ("https://t.me/%s?start=%s" % (bot.get_me().username, message.from_user.id), balance[0]))
	else:
		bot.reply_to(message, Settings.NOT_REGISTERED_MESSAGE)

@bot.message_handler(func=lambda message: True)
def do(message):
	global users_data, db_write_queue
	db = sqlite3.connect("users.db")
	c = db.cursor() # Only for read operations

	# Check if user is registered
	c.execute("SELECT null FROM USERS WHERE user_id = ?", (message.from_user.id,))
	if c.fetchone():
		bot.reply_to(message, Settings.ALREADY_REGISTERED_MESSAGE)
		return

	# Check if user is in memory
	init_user(message.from_user.id, None)
	u_step = users_data[message.from_user.id]['step']

	# Cancel registration
	if message.text == '< Cancel >':
		users_data[message.from_user.id]['step'] = 0
		bot.reply_to(message, Settings.START_MESSAGE, parse_mode='HTML', reply_markup=start_markup)
		return

	# Handle signup -> ask captcha
	elif message.text == '< Signup >' and u_step == 0:
		captcha_solution = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
		captcha = ImageCaptcha().generate(captcha_solution)
		users_data[message.from_user.id]['captcha'] = captcha_solution.lower()
		bot.send_photo(message.chat.id, captcha, Settings.ASK_CAPTCHA_MESSAGE, reply_markup=cancel_keyboard)
		users_data[message.from_user.id]['step'] = 1

	# Check captcha > ask email
	elif u_step == 1:
		if message.text.lower() == users_data[message.from_user.id]['captcha']:
			bot.reply_to(message, Settings.ASK_EMAIL_MESSAGE)
			users_data[message.from_user.id]['step'] = 2
		else:
			bot.reply_to(message, Settings.WRONG_CAPTCHA_MESSAGE)
			users_data[message.from_user.id]['step'] = 0

	# Check email -> confirm email
	elif u_step == 2:
		if re.match(Settings.EMAIL_REGEX, message.text.lower()):
			bot.reply_to(message, Settings.CONFIRM_EMAIL_MESSAGE % message.text, reply_markup=yes_no_keyboard)
			users_data[message.from_user.id]['step'] = 3
			users_data[message.from_user.id]['email'] = message.text.strip()
		else:
			bot.reply_to(message, Settings.WRONG_EMAIL_MESSAGE)
	
	# Check confirmation -> ask username
	elif u_step == 3:
		if message.text == '< Yes >':
			bot.reply_to(message, Settings.ASK_USERNAME_MESSAGE, reply_markup=cancel_keyboard)
			users_data[message.from_user.id]['step'] = 4
		elif message.text == '< No >':
			users_data[message.from_user.id]['step'] = 2
			bot.reply_to(message, Settings.ASK_EMAIL_MESSAGE, reply_markup=cancel_keyboard)
	
	# Check username -> confirm username
	elif u_step == 4:
		if re.match(Settings.USERNAME_REGEX, message.text):
			t_username = "@"+message.text.replace("@", "").strip() # Sanitize username
			bot.reply_to(message, Settings.CONFIRM_USERNAME_MESSAGE % t_username, reply_markup=yes_no_keyboard)
			users_data[message.from_user.id]['step'] = 5
			users_data[message.from_user.id]['twitter'] = t_username
		else:
			bot.reply_to(message, Settings.WRONG_USERNAME_MESSAGE)
	
	# Check confirmation -> ask erc20 address
	elif u_step == 5:
		if message.text == '< Yes >':
			bot.reply_to(message, Settings.ASK_ERC20_MESSAGE, reply_markup=cancel_keyboard)
			users_data[message.from_user.id]['step'] = 6
		elif message.text == '< No >':
			users_data[message.from_user.id]['step'] = 4
			bot.reply_to(message, Settings.ASK_USERNAME_MESSAGE, reply_markup=cancel_keyboard)
	
	# Check erc20 address -> confirm erc20 address
	elif u_step == 6:
		if re.match(Settings.ERC20_REGEX, message.text):
			bot.reply_to(message, Settings.CONFIRM_ERC20_MESSAGE % message.text, reply_markup=yes_no_keyboard)
			users_data[message.from_user.id]['step'] = 7
			users_data[message.from_user.id]['erc20'] = message.text.strip()
		else:
			bot.reply_to(message, Settings.WRONG_ERC20_MESSAGE)

	# Check confirmation -> register
	elif u_step == 7:
		if message.text == '< Yes >':
			u_data = users_data[message.from_user.id]
			ref_link = "https://t.me/%s?start=%s" % (bot.get_me().username, message.from_user.id)

			# Enqueue insert query
			db_write_queue.put(["INSERT INTO USERS VALUES (?, ?, ?, ?, ?, ?)", (
				message.from_user.id,
				Settings.REGISTRATION_BONUS,
				u_data['email'],
				u_data['twitter'],
				u_data['erc20'],
				u_data['referer']
			)])
			bot.reply_to(message, Settings.REGISTRATION_SUCCESS_MESSAGE % ref_link, reply_markup=types.ReplyKeyboardRemove())

			# Award referer (may be invalid, no one will be awarded)
			if u_data['referer'] != None:
				db_write_queue.put(["UPDATE USERS SET points = points + ? WHERE user_id = ?", (Settings.REFERER_BONUS, u_data['referer'])])

		elif message.text == '< No >':
			users_data[message.from_user.id]['step'] = 6
			bot.reply_to(message, Settings.ASK_ERC20_MESSAGE, reply_markup=cancel_keyboard)

threading.Thread(target=db_connector).start()
bot.polling()
