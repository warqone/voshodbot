from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.info_kb import info_kb
from utils.utils import load_file

info_txt = load_file('/data/info.txt')
info_router = Router()


@info_router.callback_query(F.data == "info")
async def info(call: CallbackQuery):
    await call.message.edit_text(info_txt, reply_markup=info_kb())
