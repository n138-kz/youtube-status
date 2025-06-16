from logging import getLogger,config as logging_conf
logger_config = {}
logger_config['version'] = 1
logger_config['disable_existing_loggers'] = False
logger_config['formatters'] = {}
logger_config['formatters']['simple'] = {}
logger_config['formatters']['simple']['format'] = '%(asctime)s %(name)s:%(lineno)s %(funcName)s [%(levelname)s]: %(message)s'
logger_config['formatters']['simple']['format'] = '%(asctime)s %(levelname)s: %(message)s'
logger_config['handlers'] = {}
logger_config['handlers']['consoleHandler'] = {}
logger_config['handlers']['consoleHandler']['class'] = 'logging.StreamHandler'
logger_config['handlers']['consoleHandler']['level'] = 'INFO'
logger_config['handlers']['consoleHandler']['formatter'] = 'simple'
logger_config['handlers']['consoleHandler']['stream'] = 'ext://sys.stdout'
logger_config['handlers']['fileHandler'] = {}
logger_config['handlers']['fileHandler']['class'] = 'logging.FileHandler'
logger_config['handlers']['fileHandler']['level'] = 'INFO'
logger_config['handlers']['fileHandler']['formatter'] = 'simple'
logger_config['handlers']['fileHandler']['filename'] = '/log/custom/console.log'
logger_config['loggers'] = {}
logger_config['loggers']['__main__'] = {}
logger_config['loggers']['__main__']['level'] = 'DEBUG'
logger_config['loggers']['__main__']['handlers'] = ['consoleHandler', 'fileHandler']
logger_config['loggers']['__main__']['propagate'] = False
logger_config['loggers']['same_hierarchy'] = {}
logger_config['loggers']['same_hierarchy']['level'] = 'DEBUG'
logger_config['loggers']['same_hierarchy']['handlers'] = ['consoleHandler', 'fileHandler']
logger_config['loggers']['same_hierarchy']['propagate'] = False
logger_config['loggers']['lower.sub'] = {}
logger_config['loggers']['lower.sub']['level'] = 'DEBUG'
logger_config['loggers']['lower.sub']['handlers'] = ['consoleHandler', 'fileHandler']
logger_config['loggers']['lower.sub']['propagate'] = False
logger_config['root'] = {}
logger_config['root']['level'] = 'INFO'
logging_conf.dictConfig(logger_config)
logger = getLogger(__name__)
logger.info('Init')

LOCALE = 'ja' # 言語 Language
logger.info('Locale set to {}'.format(LOCALE))

import os,sys
import hashlib
import traceback
import discord
from apiclient import discovery
from apiclient import errors as googleapiclient_errors
from dotenv import load_dotenv

load_dotenv()
TOKEN_DISCORD=os.environ['TOKEN_DISCORD']
TOKEN_YOUTUBE=os.environ['TOKEN_YOUTUBE']
if len(TOKEN_DISCORD) > 0:
    logger.info('Load & set the token DISCORD {0}..{1}'.format(
        hashlib.sha1(TOKEN_DISCORD.encode()).hexdigest()[0:7],
        hashlib.sha1(TOKEN_DISCORD.encode()).hexdigest()[-7:],
    ))
else:
    raise ValueError('Require the token.discord')
if len(TOKEN_YOUTUBE) > 0:
    logger.info('Load & set the token YOUTUBE {0}..{1}'.format(
        hashlib.sha1(TOKEN_YOUTUBE.encode()).hexdigest()[0:7],
        hashlib.sha1(TOKEN_YOUTUBE.encode()).hexdigest()[-7:],
    ))
else:
    raise ValueError('Require the token.youtube')

def getYoutubeItems(video_id='', api_service_name='youtube', api_version='v3'):
    """
    * @return :Dictionary
    """
    logger.info('Call getYoutubeItems video_id={0} api_service_name={1} api_version={2} developer_key={3}'.format(
        video_id,
        api_service_name,
        api_version,
        TOKEN_YOUTUBE,
    ))

    youtube = discovery.build(
        api_service_name,
        api_version,
        developerKey=TOKEN_YOUTUBE
    )

    try:
        response = youtube.videos().list(
            part='snippet,statistics',
            id='{},'.format(video_id)
        ).execute()
    except googleapiclient_errors.HttpError:
        logger.error(traceback.format_exc())
        logger.info('https://console.cloud.google.com/apis/credentials')
        sys.exit(1)

    snippetInfo = response["items"][0]["snippet"] # snippet
    video_title = snippetInfo['title'] # 動画タイトル
    channel_name = snippetInfo['channelTitle'] # チャンネル名

    return response

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
client = discord.Client(intents=intents)



@client.event
async def on_message(message):
    # 変数初期化
    title=None
    descr=None
    color=0x000000
    text=None

    # 送信者がbotである場合は弾く
    if message.author.bot:
        logger.warning('message author is BOT')
        return
    # テキストチャンネルのみ処理
    if message.channel.type != discord.ChannelType.text:
        logger.warning('channel type is not text channel')
        return
    # Youtube Linkのみ処理
    if not(message.content.startswith('https://')):
        logger.warning('unsupported link')
        return

# botを起動
def main():
    logger.info('Connecting to Discord API')
    try:
        client.run(TOKEN_DISCORD)
    except discord.errors.PrivilegedIntentsRequired:
        logger.error(traceback.format_exc())
        sys.exit(1)

logger.info(__name__)
if __name__ == '__main__':
    main()
