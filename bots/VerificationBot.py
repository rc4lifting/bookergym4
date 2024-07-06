from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import pyotp
import smtplib, ssl

from caches import otp_sender_email, otp_sender_password, otp_email_port
from config import bot, verification_router, logger
import database_functions, bot_messages

class VerificationBot(StatesGroup):
    start_auth = State()
    email_sent = State()
    email_verified = State()
    
    async def start_verify(message: Message, state: FSMContext):
        # TODO check if email exist in db
        
        # TODO verify the email
        
        await state.set_state(VerificationBot.start_auth)
        await bot.send_message(message.chat.id, "Sending a OTP to your email address. Please enter the OTP here when prompted. OTP is valid for 60 seconds")
        await VerificationBot.send_email(message, state)
    
    #TODO: debug this, install smtplibs, ssl
    @verification_router.message(start_auth)
    async def send_email(message: Message, state: FSMContext):
        # prep email contents and connection
        subject = bot_messages.OTP_EMAIL_SUBJECT
        receiver_email = database_functions.get_data(f"/users/{message.chat.id}/email")
    
        # set up email server
        context = ssl.create_default_context()    
        
        # create the OTP 
        base = pyotp.random_base32()
        totp = pyotp.TOTP(base, interval=60)
        await state.update_data(totp=totp)
        
        # send email with OTP
        body = bot_messages.OTP_EMAIL_MESSAGE.format(totp.now())
        
        with smtplib.SMTP_SSL("smtp.gmail.com", otp_email_port, context=context) as server:
            server.login(otp_sender_email, otp_sender_password)
            server.sendmail(otp_sender_email, receiver_email, body)
            # TODO: debug, maybe have ssl cert error

        await state.set_state(VerificationBot.email_sent)
        await message.answer("Enter your OTP here (e.g. 689594), OTP is valid for 60 seconds")
    
    @verification_router.message(email_sent)
    async def verify_email_otp(message: Message, state: FSMContext):
        user_entered_otp = message.text
        data = await state.get_data()
        totp = data['totp']
        
        if totp.verify(otp=user_entered_otp):
            await state.set_state(VerificationBot.email_sent)
            await VerificationBot.end_verification(message, state)
        else:
            await message.answer("Invalid OTP. Please try again using /verify.")
            await state.clear()
        
    @verification_router.message(email_verified)
    async def end_verification(message: Message, state: FSMContext):
        # TODO set user as verified in db
        database_functions.set_data(f"/users/{message.chat.id}/isVerified", True)
        await message.answer("Email verified successfully. You can now book a slot.")
        await state.clear()
        
        