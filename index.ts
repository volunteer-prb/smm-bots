import {TG_Update} from "./types/tg";

require('dotenv').config();
// There is no typings for telegram-bot-api module
// @ts-ignore
import TG from 'telegram-bot-api';

const sourceChannelId = process.env.SOURCE_CHANNEL_ID!.toString();
let destChannelId = process.env.DEST_CHANNEL_ID!.toString();
const adminsIds = new Set(process.env.BOT_ADMINS!.split(','));
let isActive = false;
const regex = new RegExp(process.env.REGEX_INPUT!.toString());

const api = new TG({
  token: process.env.BOT_TOKEN
});

const mp = new TG.GetUpdateMessageProvider();

api.setMessageProvider(mp);

api.start()
  .then(() => {
    console.log('API is started')
  })
  .catch(console.error);

api.on('update', (update: TG_Update) => {
  console.log('on update:\n\tupdate.message?.text = ' + update.message?.text + '\tupdate.message?.chat.id = ' + update.message?.chat.id)
  if (isActive && destChannelId && update.message?.chat.id && update.message?.chat.id.toString() === sourceChannelId && update.message?.text && regex.test(update.message.text)) {
    console.log('\tforward message')
    api.sendMessage({
      chat_id: destChannelId,
      text: update.message.text
    });
  }

  if (update.message?.chat.id.toString() !== sourceChannelId  && update.message?.from.username && adminsIds.has(update.message?.from.username)) {
    reactOnAdminCommands(update);
  }
});

function reactOnAdminCommands(update: TG_Update) {
  if (!update.message?.text) {
    return;
  }

  switch (update.message.text) {
    case "/info":
      say(update, `Я ${isActive ? 'слежу' : 'отдыхаю'}`);
      break;
    case "/start":
      if (!isActive) {
        isActive = true;
        say(update, "Теперь я слежу за сообщениями в канале");
        break;
      }
      say(update, "Я уже слежу за сообщениями в канале");
      break;
    case "/stop":
      if (isActive) {
        isActive = false;
        say(update, "Больше не буду следить за сообщениями");
        break;
      }

      say(update, "Я не слежу за сообщениями");
      break;
    default:
      api.sendMessage({
        chat_id: update.message.chat.id,
        text: `Доступные команды:\n/info\n/start\n/stop`
      });
  }
}

function say(update: TG_Update, message: string) {
  api.sendMessage({
    chat_id: update.message?.chat.id,
    text: message
  });
}
