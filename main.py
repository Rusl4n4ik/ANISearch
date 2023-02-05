from aiogram.types import ContentType, Message
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fsms import Name, Manga
from aiogram.dispatcher import FSMContext
import kitsu
from keyboard import menu
import aiogram.utils.markdown as fmt
from db import check_existing, add_user
from aiogram.utils.markdown import hlink
from prettytable import PrettyTable
import asyncio

client = kitsu.Client()
API_TOKEN = '5255963293:AAFPmVhdCPDsOnqBDzdy-qWfOdBCIqrIsmU'
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    exist_user = check_existing(message.chat.id)
    if not exist_user:
        add_user(message.chat.id, message.from_user.first_name, message.from_user.username)
        await message.answer("Kon'nichiwa " + fmt.hbold(message.from_user.username), reply_markup=menu)
        await message.answer_sticker('CAACAgIAAxkBAAEHKKtjuVjR9jdDeKOowJvDDVu-PdcYPwAC2woAAslikUlmKSeqcp2ZsC0E')
    if exist_user:
        await message.answer("Choose option from menu below:", reply_markup=menu)


@dp.message_handler(content_types=ContentType.PHOTO)
async def send_photo_id(message: Message):
    await message.reply(message.photo[-1].file_id)


@dp.message_handler(Text(equals="Search Anime"))
async def search(message: types.Message):
    await message.answer("Enter Anime name: ", reply_markup=types.ReplyKeyboardRemove())
    await Name.anime.set()


@dp.message_handler(state=Name)
async def anima(message: types.Message, state: FSMContext):
    anm = message.text
    anime = await client.search_anime(anm, limit=1)
    chat_id = message.from_user.id
    try:
        await bot.send_photo(chat_id, photo=anime.poster_image(), caption=(
            f"Canonical Title: {anime.canonical_title}\n"
            f"Title in 🇬🇧: {str(anime.title.en_jp)}\n"
            f"Title in 🇯🇵: {str(anime.title.ja_jp)}\n"
            f"Average Rating: {str(anime.average_rating)}\n"
            f"Chapters: {str(anime.episode_count)}\n\n\n"
            f"About: {str(anime.synopsis)}\n"
        ), reply_markup=menu)
        await state.finish()
    except:
        await message.answer("Something went wrong :( ", reply_markup=menu)
        await state.finish()


@dp.message_handler(Text(equals="Visit web-site"))
async def search(message: types.Message):
    kitsu = "TAP ME 👾"
    await message.answer(fmt.hlink(kitsu, "https://kitsu.io/explore/anime"), reply_markup=menu)


@dp.message_handler(Text(equals="Search Manga"))
async def search(message: types.Message):
    await message.answer("Enter Manga name: ", reply_markup=types.ReplyKeyboardRemove())
    await Manga.manga.set()


@dp.message_handler(state=Manga)
async def manha(message: types.Message, state: FSMContext):
    mng = message.text
    manga = await client.search_manga(mng, limit=1)
    # t = ("Canonical Title: " + anime.canonical_title)
    # r = ("Average Rating: " + str(anime.average_rating))
    # e = ("Episodes: " + str(anime.episode_count))
    # a = ("About: " + str(anime.synopsis))
    chat_id = message.from_user.id
    # await message.answer(
    #                      f"Canonical Title: {anime.canonical_title}\n"
    #                      f"Average Rating: {str(anime.average_rating)}\n"
    #                      f"Episodes: {str(anime.episode_count)}\n"
    #                      f"About: {str(anime.synopsis)}"
    #                      f"{anime.poster_image()}"
    #                      )
    try:
        await bot.send_photo(chat_id, photo=manga.poster_image(), caption=(
            f"Canonical Title: {manga.canonical_title}\n"
            f"Average Rating: {str(manga.average_rating)}\n"
            f"Chapters: {str(manga.chapter_count)}\n"
            f"About: {str(manga.synopsis)}"
        ), reply_markup=menu)
        await state.finish()
    except:
        await message.answer("Something went wrong :( ", reply_markup=menu)
        await state.finish()
    # await client.close()


@dp.message_handler(Text(equals="About"))
async def search(message: types.Message):
    chat_id = message.from_user.id
    await dp.bot.send_photo(chat_id=chat_id,
                            photo='AgACAgIAAxkBAAIDamPABOAvv7EdKuZEQUoL_81XN6w5AAKjyTEbqGkAAUqjHhBhEi0pJgEAAwIAA3gAAy0E',
                            caption="This bot is searching system to get info about Anime/Manga\n\nYou can receive "
                                    "data about:\n\n" + fmt.hbold("Title\nEpisides or chapters count\nAvarage Rating "
                                                                  "and also Description"))


@dp.message_handler(Text(equals="Trending Anime"))
async def trending(message: types.Message):
    data = await client.trending_anime()
    await message.answer(f"Found [{len(data)}] trending animes")
    for anime in data:
        chat_id = message.from_user.id
        await bot.send_photo(chat_id, photo=anime.poster_image())
        await message.answer("Canonical Title: " + anime.canonical_title)
        await message.answer("Average Rating: " + str(anime.average_rating))
        await message.answer("\n")


# @dp.message_handler(commands=['search'])
# async def search(message: types.Message):
#     await message.answer("Enter Anime name: ")
#     await Name.anime.set()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
