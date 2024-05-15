This is a telegram bot that parses from telegram chat messages and sends them to the GPT-3 model, then saves the response to the Notion database.

create .env file in the root of project and add the following variables:
```commandline
TGBOT_API=your api token of telegram bot
GPT_API=your api token of openai
NOTION_API=your api token of notion
NOTION_DB_ID=your database id of notion
TIME_ZONE=Europe/Moscow
```
then type "bash ./start.sh" in the terminal
