BOT_TOKEN = ""

START_MESSAGE = """<b>Welcome to dSTAR airdrop bot!</b>

Download <a href='https://dstarlab.com'>dSTAR messenger</a>
Send your telegram username to "romantrata".

Join <a href='https://t.me/dstarlab'>dSTAR telegram</a> channel

You will receive 15 TRX(TRON)

Follow <a href='https://twitter.com/dSTARLab'>dSTAR twitter</a> page, make some like, share 
You will receive 5 TRX(TRON)

Additionally, you can receive 5 TRX(TRON) for each invited user!

https://dstarlab.com"""

ADMIN_ID = 452069836

TELEGRAM_REGEX = r"^@?(\w){1,15}$"
DSTAR_REGEX = r"^@?(\w){1,40}$"
TRX_REGEX = r"^@?(\w){1,40}$"
USERNAME_REGEX = r"^@?(\w){1,15}$"

REGISTRATION_BONUS = 0
REFERER_BONUS = 5

WRONG_CAPTCHA_MESSAGE = "Wrong captcha."
WRONG_TELEGRAM_MESSAGE = "Wrong Telegram format."
WRONG_DSTAR_MESSAGE = "Wrong dSTAR format."
WRONG_USERNAME_MESSAGE = "Wrong twitter username format."
WRONG_TRX_MESSAGE = "Wrong TRX format."

CONFIRM_TELEGRAM_MESSAGE = "Do you confirm %s as your Telegram username?"
CONFIRM_DSTAR_MESSAGE = "Do you confirm %s as your dSTAR messenger username?"
CONFIRM_USERNAME_MESSAGE = "Do you confirm %s as your twitter username?"
CONFIRM_TRX_MESSAGE = "Do you confirm %s as your TRX address?"

ASK_TELEGRAM_MESSAGE = "Join dSTAR telegram channel. https://t.me/dstarlab \n\nSend me your Telegram username:"
ASK_DSTAR_MESSAGE = "Download dSTAR messenger and you will receive 15 TRX(TRON).\nhttps://dstarlab.com\nSend your telegram username to 'romantrata'!\n\nSend me your dSTAR messenger username:"
ASK_CAPTCHA_MESSAGE = "Enter the characters you see in the image"
ASK_USERNAME_MESSAGE = "Follow dSTAR twitter page, make some like, share and you will receive 5 TRX(TRON).\n https://twitter.com/dSTARLab\n\nSend me your Twitter username:"
ASK_TRX_MESSAGE = "Just one more step! Send me your TRX wallet address"

REGISTRATION_SUCCESS_MESSAGE = "Congratulations! You're registered!\nIncrease your balance by sharing this link: %s"
REGISTRATION_ABORTED_MESSAGE = "Registration aborted."
NOT_REGISTERED_MESSAGE = "You're not registered!"
BALANCE_MESSAGE = "Ref link: %s\nYour balance: %s points"
ALREADY_REGISTERED_MESSAGE = "You're already registered!"
