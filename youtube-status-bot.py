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
logger_config['handlers']['fileHandler']['level'] = 'DEBUG'
logger_config['handlers']['fileHandler']['formatter'] = 'simple'
logger_config['handlers']['fileHandler']['filename'] = '/log/custom/console.log'
logger_config['handlers']['discord'] = {}
logger_config['handlers']['discord']['class'] = 'logging.FileHandler'
logger_config['handlers']['discord']['level'] = 'DEBUG'
logger_config['handlers']['discord']['formatter'] = 'simple'
logger_config['handlers']['discord']['filename'] = '/log/custom/console.log'
logger_config['handlers']['discord.http'] = {}
logger_config['handlers']['discord.http']['class'] = 'logging.FileHandler'
logger_config['handlers']['discord.http']['level'] = 'DEBUG'
logger_config['handlers']['discord.http']['formatter'] = 'simple'
logger_config['handlers']['discord.http']['filename'] = '/log/custom/console.log'
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
import re
import hashlib
import traceback
import discord
import json
import datetime
import math
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
    logger.debug('Call getYoutubeItems video_id={0} api_info={1}:{2}'.format(
        video_id,
        api_service_name,
        api_version,
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
async def on_ready():
    logger.info('Connect OK id:{0}'.format(client.user.id))
    logger.info('Invite link: https://discord.com/oauth2/authorize?client_id={}'.format(client.user.id))

    await client.change_presence(
        status=discord.Status.online,
        activity=discord.CustomActivity(name=client.user.name)
    )
    logger.info('Change presence to {}'.format(discord.Status.online))

    # 起動完了
    logger.info('Ready')

@client.event
async def on_connect():
    logger.info('Connected')

@client.event
async def on_disconnect():
    logger.warning('Disconnected')

@client.event
async def on_error(event):
    logger.error('on_error: {}'.format(
        event,
    ))
    logger.error(sys.exc_info())

@client.event
async def on_message(message):
    # 変数初期化
    title=None
    descr=None
    color=0x000000
    color_custom={
        'success': 0x00FF00,
        'failure': 0xFF0000,
    }
    url=None
    text=None

    # 送信者が自分自身である場合は弾く
    if message.author.id == client.user.id:
        return
    # 送信者がbotである場合は弾く
    if message.author.bot:
        logger.warning('Message author is BOT')
        return
    # テキストチャンネルのみ処理
    if message.channel.type != discord.ChannelType.text:
        logger.warning('Channel type is not text channel')
        return
    # Youtube Linkのみ処理
    if not(
        message.content.startswith('https://youtu.be/')
         or message.content.startswith('https://www.youtube.com/watch?v=')
         or message.content.startswith('https://youtube.com/shorts/')
         or message.content.startswith('https://www.youtube.com/shorts/')
    ):
        logger.warning('Unsupported link: {0}'.format(
            message.content
        ))
        return

    # 変数初期化
    item_id = message.content
    
    # 複数行になってる場合最初のやつだけ
    item_id = item_id.strip()
    item_id += '\n'
    item_id = item_id.split()[0]

    # 動画URL
    url=item_id

    # メッセージ受取り
    logger.info('on_message author: {}({}) guild:{} channel:{}'.format(
        message.author.name,
        message.author.id,
        message.guild.id,
        message.channel.id,
    ))
    logger.debug('on_message author: {}({}) guild:{}({}) channel:{}({}) content:{}'.format(
        message.author.name,
        message.author.id,
        message.guild.id,
        message.guild.name,
        message.channel.id,
        message.channel.name,
        item_id,
    ))

    # 動画IDの抽出
    if False:
        pass
    elif item_id.startswith('https://youtu.be/'):
        item_id = item_id.replace('https://youtu.be/', '')
        try:
            item_id = re.sub(r'\?.*', '', item_id)
        except re.PatternError:
            logger.error(traceback.format_exc())
    elif item_id.startswith('https://www.youtube.com/watch?v='):
        item_id = item_id.replace('https://www.youtube.com/watch?v=', '')
        try:
            item_id = re.sub('&.*', '', item_id)
        except re.PatternError:
            logger.error(traceback.format_exc())
    elif item_id.startswith('https://youtube.com/shorts/'):
        item_id = item_id.replace('https://youtube.com/shorts/', '')
        try:
            item_id = re.sub(r'\?.*', '', item_id)
        except re.PatternError:
            logger.error(traceback.format_exc())
    elif item_id.startswith('https://www.youtube.com/shorts/'):
        item_id = item_id.replace('https://www.youtube.com/shorts/', '')
        try:
            item_id = re.sub(r'\?.*', '', item_id)
        except re.PatternError:
            logger.error(traceback.format_exc())

    # 動画IDの抽出
    logger.debug('item_id: {0}'.format(item_id))

    # statics取得
    youtube_video = getYoutubeItems(video_id=item_id)
    youtube_video = youtube_video['items'][0]

    # 取得した動画メタデータを保存
    if True:
        with open('/log/custom/{}.json'.format(item_id), 'w') as f:
            json.dump(youtube_video, f, sort_keys=True)

    del youtube_video['snippet']['description']
    del youtube_video['snippet']['localized']

    logger.debug(youtube_video)
    logger.debug(json.dumps(youtube_video, sort_keys=True))
    logger.debug(math.trunc(datetime.datetime.fromisoformat(youtube_video['snippet']['publishedAt']).timestamp()))

    # POST DATA
    title = '{}'.format('YouTube')
    descr = '[{}]({})'.format(
        youtube_video['snippet']['title'],
        url,
    )
    color = color_custom['success']
    image = youtube_video['snippet']['thumbnails']['default']['url']

    # Discord.Embed
    embed = discord.Embed(
        title=title, description=descr, color=color, url=url,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
    )
    try:
        embed.timestamp=datetime.datetime.fromisoformat(youtube_video['snippet']['publishedAt'])
    except discord.errors.PrivilegedIntentsRequired:
        logger.error(traceback.format_exc())
    embed.set_image(url=image)
    embed.add_field(
        inline=True,
        name=':speech_balloon:',
        value=format(int(youtube_video['statistics']['commentCount']), ','),
    )
    embed.add_field(
        inline=True,
        name=':thumbsup:',
        value=format(int(youtube_video['statistics']['likeCount']), ','),
    )
    embed.add_field(
        inline=True,
        name=':eyes:',
        value=format(int(youtube_video['statistics']['viewCount']), ','),
    )
    logger.debug( await message.reply(embed=embed) )

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
