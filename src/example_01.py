import logging
import os
from dotenv import load_dotenv

# load the .env file, ensure it loads before the swibots import
env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_file)

####
from swibots import (  # noqa
    BotApp,
    RegisterCommand,
    BotContext,
    MessageEvent,
    CallbackQueryEvent,
    CommandEvent,
    InlineMarkup,
    InlineKeyboardButton,
    InlineKeyboardColor,
    InlineKeyboardSize,
    Message,
)


TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


# initialize the app and register commands
app = BotApp(
    TOKEN, "A cool bot with annotations and everything you could possibly want :)"
).register_command(
    [
        RegisterCommand("echo", "Echoes the message", True),
        RegisterCommand("buttons", "Shows buttons", True),
    ]
)


def step_1(m:Message, params:str=None):
    m.message = f"Please select an option:"

    inline_keyboard = [
        [
            InlineKeyboardButton(text="Option 1", callback_data="option1"),
            InlineKeyboardButton(text="Option 2", callback_data="option2"),
        ],
        [
            InlineKeyboardButton(text="Option 3", callback_data="option3"),
            InlineKeyboardButton(text="Option 4", callback_data="option4"),
        ],
    ]

    color = InlineKeyboardColor.RANDOM
    size = InlineKeyboardSize.DEFAULT

    # extract color and size from params
    if params is not None and len(params) > 0:
        params = params.split(" ")
        if len(params) > 0:
            try:
                color = InlineKeyboardColor[params[0].upper()]
            except ValueError:
                pass
        if len(params) > 1:
            try:
                size = InlineKeyboardSize[params[1].upper()]
            except ValueError:
                pass

    m.inline_markup = InlineMarkup(
        inline_keyboard=inline_keyboard,
        color=color,
        size=size,
    )
    return m

def step_2(m: Message):
    m.message = f"Hello! How are you?"

    inline_keyboard = [
        [
            InlineKeyboardButton(text="Go back", callback_data="back"),
        ]
    ]

    color = InlineKeyboardColor.RANDOM
    size = InlineKeyboardSize.DEFAULT

    m.inline_markup = InlineMarkup(
        inline_keyboard=inline_keyboard,
        color=color,
        size=size,
    )
    return m

@app.on_command("buttons")
async def buttons_handler(ctx: BotContext[CommandEvent]):
    m = ctx.event.message
    # if the user is the same, edit the message
    if m.user_id == ctx.bot.id:
        m = step_1(m, ctx.event.params) # edit the message, we use the same message, without calling prepare_response_message
        await ctx.bot.edit_message(m)
    else:
        m = await ctx.bot.prepare_response_message(m) # create a new message that is a response to the original message
        m = step_1(m, ctx.event.params)
        await ctx.bot.send_message(m)


@app.on_message()
async def message_handler(ctx: BotContext[MessageEvent]):
    m = await ctx.prepare_response_message(ctx.event.message)
    m.message = f"Thank you! I received your message: {ctx.event.message.message}"
    await ctx.send_message(m)


@app.on_callback_query()
async def query_callback_handler(ctx: BotContext[CallbackQueryEvent]):
    data= ctx.event.callback_data
    if data == "back":
        m = step_1(ctx.event.message)
        await ctx.edit_message(m)
    else:
        m = step_2(ctx.event.message)
        await ctx.edit_message(m)


app.run()
