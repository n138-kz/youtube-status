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

ICONTEXT_statistics={}
ICONTEXT_statistics['default']=[
    ['v_commentCount', ':speech_balloon:'],
    ['v_likeCount', ':thumbsup:'],
    ['v_viewCount', ':eyes:'],
    ['c_subscriberCount', ':busts_in_silhouette:'],
    ['c_videoCount', ':video_camera:'],
    ['c_viewCount', ':eyes:'],
]
for list in ICONTEXT_statistics['default']:
    ICONTEXT_statistics[list[0]]=os.environ['ICONTEXT_statistics_'+list[0]]
    if len(ICONTEXT_statistics[list[0]]) == 0:
        ICONTEXT_statistics[list[0]]=list[1]

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

def getYoutubeChannels(channel_id='', api_service_name='youtube', api_version='v3'):
    """
    * @return :Dictionary
    """
    youtube = discovery.build(
        api_service_name,
        api_version,
        developerKey=TOKEN_YOUTUBE
    )

    response = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
    ).execute()

    for item in response.get("items", []):
        if item["kind"] != "youtube#channel":
            continue
        return item

dsn = 'postgresql://{}:{}@{}:{}/{}'.format(
    os.environ.get('DATABASE_DSN_username', 'postgres'),
    os.environ.get('DATABASE_DSN_password', 'postgres'),
    os.environ.get('DATABASE_DSN_hostaddr', 'localhost'),
    os.environ.get('DATABASE_DSN_portnum', 5432),
    os.environ.get('DATABASE_DSN_database', 'postgres'),
)
def store_v_info(dsn='', data={}):
    return False
def store_c_info(dsn='', data={}):
    try:
        import psycopg2
    except (ModuleNotFoundError):
        return None

    try:
        with psycopg2.connect(dsn) as conn:
            with conn.cursor() as cur:
                for item in [
                    'youtube_status_channel_thumbnails',
                    'youtube_status_channel_statistics',
                    'youtube_status_channel',
                ]:
                    sql  = ''
                    sql += 'DELETE FROM youtube_status_channel'
                    sql += ' WHERE id = %s'
                    sql += ';'
                    cur.execute(sql, (
                        data['id'],
                    ))
                sql  = ''
                sql += 'INSERT INTO youtube_status_channel'
                sql += ' ('
                sql += 'id'
                sql += ', etag'
                sql += ', kind'
                sql += ', customUrl'
                sql += ', published_at'
                sql += ', global_title'
                sql += ', global_description'
                sql += ', localized_title'
                sql += ', localized_description'
                sql += ')'
                sql += ' VALUES'
                sql += ' ('
                sql += '%s, %s, %s, %s, %s, %s, %s, %s, %s'
                sql += ')'
                sql += ';'
                if 'snippet' not in data:
                    data['snippet'] = {}
                if 'localized' not in data['snippet']:
                    data['snippet']['localized'] = {}
                data['snippet']['localized'] = {
                    **{
                        'title': None,
                        'description': None,
                    },
                    **data['snippet']['localized'],
                }
                data['snippet'] = {
                    **{
                        'customUrl': None,
                        'publishedAt': None,
                        'title': None,
                        'description': None,
                        'localized': None,
                    },
                    **data['snippet'],
                }
                logger.debug(f"id: {data['id']}")
                logger.debug(f"etag: {data['etag']}")
                logger.debug(f"kind: {data['kind']}")
                logger.debug(f"customUrl: {data['snippet']['customUrl']}")
                logger.debug(f"published_at: {datetime.datetime.fromisoformat(data['snippet']['publishedAt']).timestamp()}")
                logger.debug(f"global_title: {data['snippet']['title']}")
                logger.debug(f"global_description: {data['snippet']['description']}")
                logger.debug(f"localized_title: {data['snippet']['localized']['title']}")
                logger.debug(f"localized_description: {data['snippet']['localized']['description']}")
                cur.execute(sql, (
                    data['id'],
                    data['etag'],
                    data['kind'],
                    data['snippet']['customUrl'],
                    datetime.datetime.fromisoformat(data['snippet']['publishedAt']).timestamp(),
                    data['snippet']['title'],
                    data['snippet']['description'],
                    data['snippet']['localized']['title'],
                    data['snippet']['localized']['description'],
                ))
                sql  = ''
                sql += 'INSERT INTO youtube_status_channel_statistics'
                sql += ' ('
                sql += 'id'
                sql += ', hidden_subscriber_count'
                sql += ', subscriber_count'
                sql += ', video_count'
                sql += ', view_count'
                sql += ')'
                sql += ' VALUES'
                sql += ' ('
                sql += '%s, %s, %s, %s, %s'
                sql += ')'
                sql += ';'
                cur.execute(sql, (
                    data['id'],
                    int(data['statistics']['hiddenSubscriberCount']),
                    int(data['statistics']['subscriberCount']),
                    int(data['statistics']['videoCount']),
                    int(data['statistics']['viewCount']),
                ))
                conn.commit()
                return True
    except (Exception, psycopg2.errors.DatatypeMismatch, psycopg2.errors.NotNullViolation) as error:
        logger.error(f'Error has occured in Database operation: {error}')
        logger.error(f'{sys.exc_info()}')
        logger.error(f'{traceback.format_exc()}')
        return False

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.typing = True
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
async def on_error(event, args, kwargs):
    logger.error('on_error: {}'.format(
        event,
    ))
    logger.error(sys.exc_info())

@client.event
async def on_typing(channel, user, when):
    logger.info('on_typing: channel:{} user:{} when:{}'.format(
        channel.id,
        user.id,
        when,
    ))

@client.event
async def on_resumed():
    logger.info('resumed')

@client.event
async def on_message_edit(before, after):
    # 送信者が自分自身である場合は弾く
    if after.author.id == client.user.id:
        return
    # 送信者がbotである場合は弾く
    if after.author.bot:
        logger.warning('Message author is BOT: {}({})'.format(
            after.author.name,
            after.author.id,
        ))
        return
    # テキストチャンネルのみ処理
    if after.channel.type != discord.ChannelType.text:
        logger.warning('Channel type is not text channel')
        return
    # https Linkのみ処理
    if not(after.content.startswith('https://')):
        return
    # メッセージ受取り
    logger.info('on_message_edit author: {}({}) guild:{} channel:{}'.format(
        after.author.name,
        after.author.id,
        after.guild.id,
        after.channel.id,
    ))
    logger.debug('on_message_edit author: {}({}) guild:{}({}) channel:{}({}) content:{}'.format(
        after.author.name,
        after.author.id,
        after.guild.id,
        after.guild.name,
        after.channel.id,
        after.channel.name,
        after.content,
    ))
    # await on_message(after)

@client.event
async def on_message_delete(message):
    logger.info('on_message_delete')

@client.event
async def on_bulk_message_delete(message):
    logger.info('on_bulk_message_delete')

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
        logger.warning('Message author is BOT: {}({})'.format(
            message.author.name,
            message.author.id,
        ))
        return
    # テキストチャンネルのみ処理
    if message.channel.type != discord.ChannelType.text:
        logger.warning('Channel type is not text channel')
        return
    # https Linkのみ処理
    if not(message.content.startswith('https://')):
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
        with open('/log/custom/v_{}.json'.format(item_id), 'w') as f:
            json.dump(youtube_video, f, sort_keys=True)

    logging_mesg = youtube_video
    del logging_mesg['snippet']['description']
    del logging_mesg['snippet']['localized']

    logger.debug(logging_mesg)
    logger.debug(json.dumps(logging_mesg, sort_keys=True))
    logger.debug(math.trunc(datetime.datetime.fromisoformat(logging_mesg['snippet']['publishedAt']).timestamp()))

    # youtube-channel statics取得
    youtube_channel = getYoutubeChannels(youtube_video['snippet']['channelId'])

    # 取得したチャンネルメタデータを保存
    if True:
        with open('/log/custom/c_{}.json'.format(youtube_video['snippet']['channelId']), 'w') as f:
            json.dump(youtube_channel, f, sort_keys=True)

    logging_mesg = youtube_channel
    del logging_mesg['snippet']['description']
    del logging_mesg['snippet']['localized']

    logger.debug(logging_mesg)
    logger.debug(json.dumps(logging_mesg, sort_keys=True))

    # 取得したデータをデータベースに保存
    logger.debug(store_c_info(dsn=dsn, data=youtube_channel))
    logger.debug(store_v_info(dsn=dsn, data=youtube_video))

    # POST DATA
    title = '{}'.format('YouTube')
    descr = '[{}]({})'.format(
        youtube_video['snippet']['title'],
        url,
    )
    color = color_custom['success']
    image = youtube_video['snippet']['thumbnails']['default']['url']
    try:
        image = youtube_video['snippet']['thumbnails']['high']['url']
    except (NameError,KeyError):
        pass
    try:
        image = youtube_video['snippet']['thumbnails']['standard']['url']
    except (NameError,KeyError):
        pass
    try:
        image = youtube_video['snippet']['thumbnails']['maxres']['url']
    except (NameError,KeyError):
        pass

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
        name=ICONTEXT_statistics['v_commentCount'],
        value=format(int(youtube_video['statistics']['commentCount']), ','),
    )
    embed.add_field(
        inline=True,
        name=ICONTEXT_statistics['v_likeCount'],
        value=format(int(youtube_video['statistics']['likeCount']), ','),
    )
    embed.add_field(
        inline=True,
        name=ICONTEXT_statistics['v_viewCount'],
        value=format(int(youtube_video['statistics']['viewCount']), ','),
    )
    embed.add_field(
        inline=True,
        name=ICONTEXT_statistics['c_subscriberCount'],
        value=format(int(youtube_channel['statistics']['subscriberCount']), ','),
    )
    embed.add_field(
        inline=True,
        name=ICONTEXT_statistics['c_videoCount'],
        value=format(int(youtube_channel['statistics']['videoCount']), ','),
    )
    embed.add_field(
        inline=True,
        name=ICONTEXT_statistics['c_viewCount'],
        value=format(int(youtube_channel['statistics']['viewCount']), ','),
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
