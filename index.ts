import {TG_Update} from "./types/tg";

require('dotenv').config();
// There is no typings for telegram-bot-api module
// @ts-ignore
import TG from 'telegram-bot-api';
import {twitterBot} from "./twitter-bot";

twitterBot();
//
//
// const sourceChannelId = process.env.SOURCE_CHANNEL_ID;
// let destChannelId = process.env.DEST_CHANNEL_ID;
// const adminsIds = new Set(process.env.BOT_ADMINS?.split(','));
// let isActive = false;
//
// const api = new TG({
//   token: process.env.BOT_TOKEN
// });
//
// const mp = new TG.GetUpdateMessageProvider();
//
// api.setMessageProvider(mp);
//
// api.start()
//   .then(() => {
//     console.log('API is started')
//   })
//   .catch(console.error);
//
// api.on('update', (update: TG_Update) => {
//   if (isActive && destChannelId && update.message?.chat.id && update.message?.chat.id === sourceChannelId) {
//     api.sendMessage({
//       chat_id: destChannelId,
//       text: update.message.text
//     });
//   }
//
//   if (update.message?.from.username && adminsIds.has(update.message?.from.username)) {
//     reactOnAdminCommands(update);
//   }
// });
//
// function reactOnAdminCommands(update: TG_Update) {
//   if (!update.message?.text) {
//     return;
//   }
//
//   switch (update.message.text) {
//     case "/info":
//       say(update, `Я ${isActive ? 'слежу' : 'отдыхаю'}`);
//       break;
//     case "/start":
//       if (!isActive) {
//         isActive = true;
//         say(update, "Теперь я слежу за сообщениями в канале");
//         break;
//       }
//       say(update, "Я уже слежу за сообщениями в канале");
//       break;
//     case "/stop":
//       if (isActive) {
//         isActive = false;
//         say(update, "Больше не буду следить за сообщениями");
//         break;
//       }
//
//       say(update, "Я не слежу за сообщениями");
//       break;
//     default:
//       api.sendMessage({
//         chat_id: update.message.chat.id,
//         text: `Доступные команды:\n/info\n/start\n/stop`
//       });
//   }
// }
//
// function say(update: TG_Update, message: string) {
//   api.sendMessage({
//     chat_id: update.message?.chat.id,
//     text: message
//   });
// }
