from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import pyotp
import resend

from caches import resend_api_key
from config import bot, verification_router, logger
import database_functions, bot_messages, utils

class VerificationBot(StatesGroup):
    email_confirmation = State()
    start_auth = State()
    email_sent = State()
    email_verified = State()
    
    async def start_verify(message: Message, state: FSMContext):
        logger.info("1: Verification started!")
        if database_functions.user_is_verified(message.chat.id):
            logger.error("verification - user already verified")
            await bot.send_message(message.chat.id, "You are already verified :)")
            await state.clear()
            return
        
        receiver_email = database_functions.read_data(f"/users/{message.chat.id}/email")
        
        if receiver_email is None:
            logger.error("verification - no valid email in database")
            await bot.send_message(message.chat.id, "No valid email given, please register with /register.")
            await state.clear()
            return
        
        await state.update_data(email=receiver_email)
        
        # set up details confirmation
        confirm_options = {
            "Yes": "CONFIRM",
            "No": "CANCEL"
        }
        
        await state.set_state(VerificationBot.email_confirmation)
        await message.answer(
            f"Your email address is: \n {receiver_email}\n\n Do you want to confirm this email address?", 
            reply_markup=utils.create_inline(confirm_options, row_width=2)
        )
    
    @verification_router.callback_query(email_confirmation)
    async def confirm_email(callback_query: CallbackQuery, state: FSMContext):
        logger.info("2: Confirming Email!")
        message = callback_query.message
        
        if callback_query.data != "CONFIRM":
            logger.error("verification - invalid/ CANCEL option received!")
            await bot.send_message(message.chat.id, "Email verification cancelled, please re-register with new details at /register.")
            await state.clear()
        else: 
            await state.set_state(VerificationBot.start_auth)
            await bot.send_message(message.chat.id, "Sending a OTP to your email address. Please enter the OTP here when prompted. OTP is valid for 60 seconds")
            await VerificationBot.send_email(message, state)
    
    @verification_router.message(start_auth)
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
            await state.set_state(VerificationBot.email_sent)
            await message.answer("Enter your OTP here (e.g. 689594)\n\n Check your junk email folder too!")
    
    @verification_router.message(email_sent)
    async def verify_email_otp(message: Message, state: FSMContext):
        user_entered_otp = message.text
        data = await state.get_data()
        totp = data['totp']
        
        if totp.verify(otp=user_entered_otp):
            await state.set_state(VerificationBot.email_sent)
            await VerificationBot.end_verification(message, state)
            logger.info("EMAIL VERIFIED")
        else:
            logger.info("INVALID OTP by user")
            await message.answer("Invalid OTP. Please try again using /verify.")
            await state.clear()
        
    @verification_router.message(email_verified)
    async def end_verification(message: Message, state: FSMContext):
        database_functions.set_data(f"/users/{message.chat.id}/isVerified", True)
        logger.info("USER IS VERIFIED")
        await message.answer("Email verified successfully. You can now book a slot with /book.")
        await state.clear()
        
        