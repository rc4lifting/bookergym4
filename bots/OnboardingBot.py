from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

import pyotp
import resend

from caches import resend_api_key
from config import bot, onboarding_router, logger
import database_functions, bot_messages, utils, re

class OnboardingBot(StatesGroup):
    get_nusnet = State()
    check_nusnet = State()
    get_email = State()
    check_email = State()
    email_confirmation = State()
    start_auth = State()
    email_sent = State()
    email_verified = State()
    
    ## Registration Portion
    # pdpa consent
    async def start_register(message: Message, state: FSMContext):
        logger.info("1: Registration started!")
        
        # TODO: to move adding user to db in /register command
        if database_functions.user_is_registered(message.chat.id):
            await message.answer("You have already registered! Please verify your email using /verify.")
            await state.clear()
            return
        
        await state.set_state(OnboardingBot.get_nusnet)
        await bot.send_message(message.chat.id, bot_messages.PDPA_PRECLAUSE_MESSAGE, parse_mode=ParseMode.HTML)
        await bot.send_message(message.chat.id, bot_messages.PDPA_CLAUSE_MESSAGE, parse_mode=ParseMode.HTML)
        await message.answer(bot_messages.PDPA_QUESTION_MESSAGE, reply_markup=utils.create_inline({"I consent": "CONSENT"}, row_width=2))
    
    # get nus net id 
    @onboarding_router.callback_query(get_nusnet)
    async def nusnet_id_callback(callback_query: CallbackQuery, state: FSMContext):
        message = callback_query.message
        
        if callback_query.data != "CONSENT":
            await bot.send_message(message.chat.id, "Please consent to the PDPA clause to continue. Read the clause and select 'I consent' to continue.")
            return
        
        telehandle = callback_query.from_user.username
        data = {
            "telehandle": f"{telehandle}",
            "isVerified": False
        }
        database_functions.create_data(f"/users/{message.chat.id}", data)
        logger.info("user consent pdpa and added to db")
        
        await state.set_state(OnboardingBot.check_nusnet)
        await message.answer("Please enter your NUSNET ID:\n (e.g. E1234567)")
    
    @onboarding_router.message(check_nusnet)
    async def nusnet_checking(message: Message, state: FSMContext):
        nusnet = message.text
        if not re.match(r"^[eE]\d{7}$", nusnet):
            logger.info("Invalid NUSNET Received!")
            await message.answer("NUSNET ID not valid, please re-enter your NUSNET ID (e.g. E1234567)")
            return
        
        logger.info("Valid NUSNET")
        database_functions.set_data(f"/users/{message.from_user.id}/nusnet", nusnet)
        await state.set_state(OnboardingBot.get_email)
        await OnboardingBot.collect_email(message, state)
    
    # get nus email
    @onboarding_router.message(get_email)
    async def collect_email(message: Message, state: FSMContext):
        await state.set_state(OnboardingBot.check_email)
        await message.answer("Please enter your NUS email:\n")
        
    @onboarding_router.message(check_email)
    async def email_checking(message: Message, state: FSMContext):
        email = message.text
        if not re.match(r".*@u\.nus\.edu$", email):
            logger.info("Invalid Email Received!")
            await message.answer("Invalid email format. Please enter a valid NUS email:\n (e.g. E1234567@u.nus.edu)")
            return
        
        logger.info("Valid NUS Email")
        database_functions.set_data(f"/users/{message.from_user.id}/email", email)
        await bot.send_message(message.chat.id, "Email registered successfully! Please verify your details using /verify.")
        await state.clear()
        
    ## Verification Portion
    async def start_verify(message: Message, state: FSMContext):
        logger.info("1: Verification started!")
        if database_functions.user_is_verified(message.chat.id):
            logger.info("verification - user already verified")
            await bot.send_message(message.chat.id, "You are already verified :)")
            await state.clear()
            return
        
        received_nusnet = database_functions.read_data(f"/users/{message.chat.id}/nusnet")
        received_email = database_functions.read_data(f"/users/{message.chat.id}/email")
        
        if received_nusnet is None:
            logger.error("verification - no valid nusnet in database")
            await bot.send_message(message.chat.id, "No valid NUSNET ID given, please register with /register.")
            await state.clear()
            return
        
        if received_email is None:
            logger.error("verification - no valid email in database")
            await bot.send_message(message.chat.id, "No valid email given, please register with /register.")
            await state.clear()
            return
        
        await state.update_data(nusnet=received_nusnet)
        await state.update_data(email=received_email)
        
        # set up details confirmation
        confirm_options = {
            "Yes": "CONFIRM",
            "No": "CANCEL"
        }
        
        await state.set_state(OnboardingBot.email_confirmation)
        await message.answer(
            f"Your NUSNET ID is: {received_nusnet}\n\n Your email address is: \n {received_email}\n\n Do you want to confirm these details?", 
            reply_markup=utils.create_inline(confirm_options, row_width=2)
        )
    
    @onboarding_router.callback_query(email_confirmation)
    async def confirm_email(callback_query: CallbackQuery, state: FSMContext):
        logger.info("2: Confirming Email!")
        message = callback_query.message
        
        if callback_query.data != "CONFIRM":
            logger.error("verification - invalid/ CANCEL option received!")
            await bot.send_message(message.chat.id, "Email verification cancelled, please re-register with new details at /register.")
            await state.clear()
        else: 
            await state.set_state(OnboardingBot.start_auth)
            await bot.send_message(message.chat.id, "Sending a OTP to your email address. Please enter the OTP here when prompted. OTP is valid for 60 seconds")
            await OnboardingBot.send_email(message, state)
    
    @onboarding_router.message(start_auth)
    async def send_email(message: Message, state: FSMContext):
        logger.info("3: preparing otp email")
        # prep email contents and connection
        data = await state.get_data()
        receiver_email = data['email']
    
        # set up email server  
        resend.api_key = resend_api_key 
        
        # create the OTP 
        base = pyotp.random_base32()
        totp = pyotp.TOTP(base, interval=120) 
        await state.update_data(totp=totp)
        
        # send email with OTP
        params: resend.Emails.SendParams = {
            "from": "otp@rc4lifting.xyz",
            "to": [receiver_email],
            "subject": bot_messages.OTP_EMAIL_SUBJECT,
            "text": bot_messages.OTP_EMAIL_MESSAGE.format(totp.now()),
        }
        
        try:
            logger.info("4: sending otp email")
            email = resend.Emails.send(params)
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            await message.answer("Error sending email. Please try again later.")
            await state.clear()
        else:
            logger.info("VERIFICATION EMAIL SENT")
            await state.set_state(OnboardingBot.email_sent)
            await message.answer("Enter your OTP here (e.g. 689594)\n\n Check your junk email folder too!")
    
    @onboarding_router.message(email_sent)
    async def verify_email_otp(message: Message, state: FSMContext):
        user_entered_otp = message.text
        data = await state.get_data()
        totp = data['totp']
        
        if totp.verify(otp=user_entered_otp):
            await state.set_state(OnboardingBot.email_sent)
            await OnboardingBot.end_verification(message, state)
            logger.info("EMAIL VERIFIED")
        else:
            logger.info("INVALID OTP by user")
            await message.answer("Invalid OTP. Please try again using /verify.")
            await state.clear()
        
    @onboarding_router.message(email_verified)
    async def end_verification(message: Message, state: FSMContext):
        database_functions.set_data(f"/users/{message.chat.id}/isVerified", True)
        logger.info("USER IS VERIFIED")
        await message.answer("Email verified successfully. You can now book a slot with /book.")
        await state.clear()
        
        