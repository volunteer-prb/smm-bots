import needle, {BodyData} from "needle";
import dotenv from 'dotenv';
import {Telegraf, Context} from "telegraf";
import {ForceReply} from "typegram/markup";
import {InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove} from "telegraf/typings/core/types/typegram";
import {Readable} from "stream";
import moment from "moment";

dotenv.config();

const {
  TWITTER_BOT_API_URL,
  SOURCE_CHANNEL_ID,
  DEST_CHANNEL_ID,
  BOT_ADMINS,
  REGEX_INPUT,
  BOT_TOKEN
} = process.env;

const sourceChannelId = SOURCE_CHANNEL_ID?.toString();
let destChannelId = DEST_CHANNEL_ID?.toString();
const adminsIds = new Set(BOT_ADMINS?.split(','));
let isTgActive = false;
let isTwActive = false;
const regex = new RegExp(REGEX_INPUT?.toString() || '');
const pins: { [name: string]: string } = {};

const PIN_MESSAGE = "Пин: ";

if (!BOT_TOKEN) {
  throw "Can't start without bot token";
}

const api = new Telegraf(BOT_TOKEN);

startTgListening();

api.on('callback_query', async (ctx) => {
  const chat = ctx.callbackQuery.message?.chat;
  console.log(ctx.callbackQuery.message);

  if (chat && chat.type === "private" && chat.username) {
    let pinFinished = false;
    if(ctx.callbackQuery.data === "enter") {
      pinFinished = true
    } else if(ctx.callbackQuery.data === "clear") {
      pins[chat.username] = ''
    } else {
      pins[chat.username] = (pins[chat.username] || '') + ctx.callbackQuery.data;
    }
    await ctx.telegram.editMessageText(chat.id, ctx.callbackQuery.message?.message_id, undefined, PIN_MESSAGE + pins[chat.username], {
      reply_markup: pinFinished ? undefined : getNumbersKeyboard()
    });

    try {
      if (pinFinished) {
        console.log(pins[chat.username]);
        await twitterBotClient('start', {verifier: pins[chat.username]});
        isTwActive = true;
        say(ctx, `Теперь я слежу за сообщениями в Твиттере`);
        pins[chat.username] = '';
      }
    } catch (e) {
      twitterApiAccessError(ctx, e);
      ctx.answerCbQuery();
      return;
    }
  }

  ctx.answerCbQuery();
});


api.on('text', (ctx, next) => {
  console.log('on update:\n\tupdate.message?.text = ' + ctx.message?.text + '\tupdate.message?.chat.id = ' + ctx.message?.chat.id);
  if (isTgActive && destChannelId && ctx.message?.chat.id && ctx.message?.chat.id.toString() === sourceChannelId && ctx.message?.text && regex.test(ctx.message.text)) {
    console.log('\tforward message');
    ctx.telegram.sendMessage(destChannelId, ctx.message.text);
  }

  if (ctx.message?.chat.type === 'private' && ctx.message?.from.username && adminsIds.has(ctx.message?.from.username)) {
    next();
  }
});

function startTgListening() {
  api.launch({dropPendingUpdates: true});
}

function twitterBotClient(command: string, data?: BodyData) {
  const url = TWITTER_BOT_API_URL?.toString() + command;
  if (data) {
    return needle('post', url, data, {json: true})
  } else {
    return needle('get', url)
  }
}

// Telegram specific commands
api.command("infotg", (ctx) => {
  say(ctx, `Я ${isTgActive ? 'слежу' : 'отдыхаю'}`);
});

api.command("starttg", (ctx) => {
  if (!isTgActive) {
    isTgActive = true;
    say(ctx, "Теперь я слежу за сообщениями в Телеграм канале");
    return;
  }
  say(ctx, "Я уже слежу за сообщениями в Телеграм канале");
});

api.command("stoptg", (ctx) => {
  if (isTgActive) {
    isTgActive = false;
    say(ctx, "Больше не буду следить за сообщениями в Телеграм");
    return;
  }

  say(ctx, "Я не слежу за сообщениями  в Телеграм");
});

// Twitter specific commands
api.command("infotw", async (ctx) => {
  try {
    const result = await twitterBotClient('status');
    say(ctx, `Текущий статус Твиттер бота: ${result.body.status}`);
  } catch (e) {
    twitterApiAccessError(ctx, e);
  }
});

api.command("starttw", async (ctx) => {
  if (ctx.message.from.username && !isTwActive) {
    try {
      const result = await twitterBotClient('authorization-url');
      pins[ctx.message.from.username] = '';
      say(ctx, `[Получите пин и введите его](${result.body.url})`);
      say(ctx, "Пин: ", getNumbersKeyboard());
    } catch (e) {
      twitterApiAccessError(ctx, e);
    }
    return;
  }
  say(ctx, "Я уже слежу за сообщениями в Твиттере");
});

api.command("stoptw", async (ctx) => {
  if (isTwActive) {
    await twitterBotClient('stop', {});
    isTwActive = false;
    try {
      say(ctx, "Больше не буду следить за сообщениями в Твиттере");
    } catch (e) {
      twitterApiAccessError(ctx, e);
    }
  }

  say(ctx, "Я не слежу за сообщениями в Твиттере");
});

api.command('printtw', async (ctx) => {
  const [, dateStr] = ctx.update.message.text.split(" ");

  say(ctx, `Запрашиваю, подождите...`);
  const date = [
    "DD-MM-YYYY",
    "DD.MM.YYYY",
    "DD/MM/YYYY",
  ].reduce((result, format) => {
    const tmpDate = moment(dateStr, format);

    return tmpDate.isValid() ? tmpDate : result;
  }, moment());

  try {

    const result = await twitterBotClient(`list/html?time=${date.format("DD-MM-YYYY")}`);

    const stream = new Readable();
    stream.push(result.body);
    stream.push(null);

    await api.telegram.sendDocument(ctx.chat.id, {source: stream, filename: `output_${date.format('DD_MM_YYYY')}.html`});
  } catch (e) {
    twitterApiAccessError(ctx, e);
  }
});

api.on('text', (ctx) => {
  say(ctx, `Доступные команды:\n/infotg\n/infotw\n/starttg\n/stoptg\n/starttw\n/stoptw\n/printtw`);
});

function say(ctx: Context, message: string, reply_markup:
  | InlineKeyboardMarkup
  | ReplyKeyboardMarkup
  | ReplyKeyboardRemove
  | ForceReply = {remove_keyboard: true}) {
  if (!ctx.message?.chat.id) {
    return;
  }

  return api.telegram.sendMessage(ctx.message?.chat.id, message.replace(/\./g, '\\.'), {
    parse_mode: "MarkdownV2",
    reply_markup
  })
    .catch(console.error);
}

function getNumbersKeyboard(): InlineKeyboardMarkup {
  return {
    inline_keyboard: [
      [{text: '1', callback_data: "1"},
        {text: '2', callback_data: "2"},
        {text: '3', callback_data: "3"},
        {text: '4', callback_data: "4"},
        {text: '5', callback_data: "5"}],
      [{text: '6', callback_data: "6"},
        {text: '7', callback_data: "7"},
        {text: '8', callback_data: "8"},
        {text: '9', callback_data: "9"},
        {text: '0', callback_data: "0"}],
      [{text: 'Enter', callback_data: "enter"},
        {text: 'Clear', callback_data: "clear"}]
    ]
  };
}

function twitterApiAccessError(ctx: Context, e: unknown) {
  console.error("Twitter API is not responding", e);
  say(ctx, "Кажется, твиттер бот не отвечает... Пожалуйста, сообщите Администратору.");
}
