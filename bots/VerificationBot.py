from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from config import bot, verification_router, logger
import database_functions, utils, bot_messages

class VerificationBot(StatesGroup):
    start_auth = State()
    email_sent = State()
    email_verified = State()
    
    async def start_verify(message: Message, state: FSMContext):
        # TODO check if email exist in db
        
        # TODO check if email is verified
        
        await state.set_state(VerificationBot.start_auth)
        await bot.send_message(message.chat.id, "Sending a OTP to your email address. Please enter the OTP here when prompted. OTP is valid for 60 seconds")
    
    @verification_router.message(start_auth)
    async def send_email(message: Message, state: FSMContext):
        # TODO else send OTP to email
        
        await state.set_state(VerificationBot.email_sent)
        await message.answer("Enter your OTP here (e.g. 689594), OTP is valid for 60 seconds")
    
    @verification_router.message(email_sent)
    async def verify_email_otp(message: Message, state: FSMContext):
        # TODO check OTP logic here
        
        await state.set_state(VerificationBot.email_sent)
        await VerificationBot.end_verification(message, state)
        
    @verification_router.message(email_verified)
    async def end_verification(message: Message, state: FSMContext):
        # TODO set user as verified in db
        database_functions.set_data(f"/users/{message.chat.id}/isVerified", True)
        await message.answer("Email verified successfully. You can now book a slot.")
        await state.clear()
        
        