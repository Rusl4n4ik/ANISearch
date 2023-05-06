import aiogram, kitsu, asyncio, random, requests, json, giphy_client, aiohttp
from aiogram.types import ContentType, Message
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fsms import Name, Manga, Character
from aiogram.dispatcher import FSMContext
from keyboard import menu
from db import check_existing, add_user
import aiogram.utils.markdown as fmt
from googletrans import Translator


client = kitsu.Client()
API_TOKEN = '5255963293:AAFPmVhdCPDsOnqBDzdy-qWfOdBCIqrIsmU'
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
giphy_api_key = "WN2wTCexCkLA6SbotqtjOq6Dy4yVsY6C"
api_instance = giphy_client.DefaultApi()


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


@dp.message_handler(Text(equals="⟡Search Anime⟡"))
async def search(message: types.Message):
    await message.answer("Enter Anime name: ", reply_markup=types.ReplyKeyboardRemove())
    await Name.anime.set()


@dp.message_handler(state=Name)
async def anima(message: types.Message, state: FSMContext):
    anm = message.text
    anime = await client.search_anime(anm, limit=1)
    chat_id = message.from_user.id
    try:
        animego_link = f"https://animego.org/anime/{anime.id}"
        caption = (
            f"Canonical Title: {anime.canonical_title}\n"
            f"Title in 🇬🇧: {str(anime.title.en_jp)}\n"
            f"Title in 🇯🇵: {str(anime.title.ja_jp)}\n"
            f"Average Rating: {str(anime.average_rating)}\n"
            f"Chapters: {str(anime.episode_count)}\n\n\n"
            f"About: {str(anime.synopsis)}\n\n"
            f"Watch on Animego: {animego_link}"
        )
        await bot.send_photo(chat_id, photo=anime.poster_image(), caption=caption, reply_markup=menu)
        await state.finish()
    except:
        await message.answer("Something went wrong :( ", reply_markup=menu)
        await state.finish()


@dp.message_handler(Text(equals="⟡Visit web-site⟡"))
async def search(message: types.Message):
    kitsu = "TAP ME 👾"
    await message.answer(fmt.hlink(kitsu, "https://kitsu.io/explore/anime"), reply_markup=menu)


@dp.message_handler(Text(equals="⟡Search Manga⟡"))
async def search(message: types.Message):
    await message.answer("Enter Manga name: ", reply_markup=types.ReplyKeyboardRemove())
    await Manga.manga.set()


@dp.message_handler(state=Manga)
async def manha(message: types.Message, state: FSMContext):
    mng = message.text
    manga = await client.search_manga(mng, limit=1)
    chat_id = message.from_user.id
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


@dp.message_handler(Text(equals="⟡About⟡"))
async def search(message: types.Message):
    chat_id = message.from_user.id
    await dp.bot.send_photo(chat_id=chat_id,
                            photo='AgACAgIAAxkBAAIDamPABOAvv7EdKuZEQUoL_81XN6w5AAKjyTEbqGkAAUqjHhBhEi0pJgEAAwIAA3gAAy0E',
                            caption="This bot is searching system to get info about Anime/Manga\n\nYou can receive "
                                    "data about:\n\n" + fmt.hbold("Title\nEpisides or chapters count\nAvarage Rating "
                                                                  "and also Description"))


@dp.message_handler(Text(equals="⟡Trending Anime⟡"))
async def trending(message: types.Message):
    data = await client.trending_anime()
    await message.answer(f"Found [{len(data)}] trending animes")
    for anime in data:
        chat_id = message.from_user.id
        try:
            await bot.send_photo(chat_id, photo=anime.poster_image(),
                                 caption="Canonical Title: " + anime.canonical_title + "\n" +
                                         "Average Rating: " + str(anime.average_rating) + "\n")
        except aiogram.utils.exceptions.WrongFileIdentifier:
            await message.answer("Canonical Title: " + anime.canonical_title + "\n" +
                                  "Average Rating: " + str(anime.average_rating) + "\n")


@dp.message_handler(Text(equals="⟡Trending Manga⟡"))
async def trending(message: types.Message):
    data = await client.trending_manga()
    await message.answer(f"Found [{len(data)}] trending manga")
    for manga in data:
        chat_id = message.from_user.id
        await bot.send_photo(chat_id, photo=manga.poster_image(),
                             caption=f"Canonical Title: {manga.canonical_title}\n"
                                     f"Average Rating: {manga.average_rating}\n")


def search_character(query):
    url = f"https://kitsu.io/api/edge/characters?filter[name]={query}"
    headers = {'Accept': 'application/vnd.api+json',
               'Content-Type': 'application/vnd.api+json'}
    response = requests.get(url, headers=headers)
    data = response.json()
    if data and data["data"]:
        character = data["data"][0]
        character_name = character["attributes"]["name"]
        character_description = character["attributes"]["description"]
        character_image_url = character["attributes"]["image"]["original"]
        return character_name, character_description, character_image_url
    else:
        return None, None, None


@dp.message_handler(Text(equals="⟡Search Character⟡"))
async def character_handler_start(message: types.Message):
    await message.answer("Enter character name:")
    await Character.char.set()


@dp.message_handler(state=Character.char)
async def character_handler_query(message: types.Message, state: FSMContext):
    query = message.text
    if query:
        character_name, character_description, character_image_url = search_character(query)
        if character_name and character_description and character_image_url:
            await bot.send_photo(message.chat.id, character_image_url)
            await bot.send_message(message.chat.id, f"Character: {character_name}")
            max_message_length = 4096
            chunks = [character_description[i:i + max_message_length] for i in
                      range(0, len(character_description), max_message_length)]
            for chunk in chunks:
                await bot.send_message(message.chat.id, chunk)
                await asyncio.sleep(1)
        else:
            await message.answer("Character not found.")
        await state.finish()
    else:
        await message.answer("Please provide a character name.")


def get_anime_gif():
    url = f"https://api.giphy.com/v1/gifs/random?api_key=WN2wTCexCkLA6SbotqtjOq6Dy4yVsY6C&tag=anime"
    response = requests.get(url)
    data = json.loads(response.text)
    return data["data"]["images"]["original"]["url"]


@dp.message_handler(Text(equals="⟡Random AniGIF⟡"))
async def send_anime_gif(message: types.Message):
    chat_id = message.chat.id
    gif_url = get_anime_gif()
    await bot.send_animation(chat_id, animation=gif_url)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
