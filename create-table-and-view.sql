-- drop
DROP VIEW IF EXISTS public.youtube_status_video_view;
DROP VIEW IF EXISTS public.youtube_status_channel_view;
DROP TABLE IF EXISTS youtube_status_video_thumbnails;
DROP TABLE IF EXISTS youtube_status_video_statistics;
DROP TABLE IF EXISTS youtube_status_video;
DROP TABLE IF EXISTS youtube_status_channel_thumbnails;
DROP TABLE IF EXISTS youtube_status_channel_statistics;
DROP TABLE IF EXISTS youtube_status_channel;
-- channel
-- https://developers.google.com/youtube/v3/docs/channels?hl=ja#properties
CREATE TABLE IF NOT EXISTS youtube_status_channel (
  "timestamp" double precision NOT NULL DEFAULT EXTRACT(epoch FROM CURRENT_TIMESTAMP),
  id text NOT NULL, -- channel id
  etag text NOT NULL,
  kind text NOT NULL,
  customUrl text,
  published_at double precision NOT NULL DEFAULT EXTRACT(epoch FROM CURRENT_TIMESTAMP),
  global_title text NOT NULL,
  global_description text,
  localized_title text,
  localized_description text,
  CONSTRAINT youtube_status_channel_pkey PRIMARY KEY (id)
);
ALTER TABLE IF EXISTS public.youtube_status_channel OWNER to webapp;
CREATE TABLE IF NOT EXISTS youtube_status_channel_thumbnails (
  "timestamp" double precision NOT NULL DEFAULT EXTRACT(epoch FROM CURRENT_TIMESTAMP),
  id text NOT NULL, -- channel id
  default_url text,
  default_width int NOT NULL DEFAULT 0,
  default_height int NOT NULL DEFAULT 0,
  medium_url text,
  medium_width int NOT NULL DEFAULT 0,
  medium_height int NOT NULL DEFAULT 0,
  high_url text,
  high_width int NOT NULL DEFAULT 0,
  high_height int NOT NULL DEFAULT 0,
  standard_url text,
  standard_width int NOT NULL DEFAULT 0,
  standard_height int NOT NULL DEFAULT 0,
  maxres_url text,
  maxres_width int NOT NULL DEFAULT 0,
  maxres_height int NOT NULL DEFAULT 0,
  FOREIGN KEY(id) REFERENCES youtube_status_channel(id),
  CONSTRAINT youtube_status_channel_thumbnails_pkey PRIMARY KEY (id)
);
ALTER TABLE IF EXISTS public.youtube_status_channel_thumbnails OWNER to webapp;
CREATE TABLE IF NOT EXISTS youtube_status_channel_statistics (
  "timestamp" double precision NOT NULL DEFAULT EXTRACT(epoch FROM CURRENT_TIMESTAMP),
  id text NOT NULL, -- channel id
  hidden_subscriber_count boolean NOT NULL DEFAULT false,
  subscriber_count int NOT NULL DEFAULT 0, -- need str to int
  video_count int NOT NULL DEFAULT 0, -- need str to int
  view_count int NOT NULL DEFAULT 0, -- need str to int
  FOREIGN KEY(id) REFERENCES youtube_status_channel(id),
  CONSTRAINT youtube_status_channel_statistics_pkey PRIMARY KEY (id)
);
ALTER TABLE IF EXISTS public.youtube_status_channel_statistics OWNER to webapp;
-- video
-- https://developers.google.com/youtube/v3/docs/videos?hl=ja#properties
CREATE TABLE IF NOT EXISTS youtube_status_video (
  "timestamp" double precision NOT NULL DEFAULT EXTRACT(epoch FROM CURRENT_TIMESTAMP),
  id text NOT NULL, -- video id
  etag text NOT NULL,
  kind text NOT NULL,
  category_id text NOT NULL,
  channel_id text NOT NULL, -- [fkey] channel id
  default_audio_language text NOT NULL DEFAULT 'en',
  live_broadcast_content text NOT NULL,
  published_at double precision NOT NULL DEFAULT EXTRACT(epoch FROM CURRENT_TIMESTAMP),
  global_title text NOT NULL,
  global_description text,
  localized_title text,
  localized_description text,
  FOREIGN KEY(channel_id) REFERENCES youtube_status_channel(id),
  CONSTRAINT youtube_status_video_pkey PRIMARY KEY (id)
);
ALTER TABLE IF EXISTS public.youtube_status_video OWNER to webapp;
CREATE TABLE IF NOT EXISTS youtube_status_video_thumbnails (
  "timestamp" double precision NOT NULL DEFAULT EXTRACT(epoch FROM CURRENT_TIMESTAMP),
  id text NOT NULL, -- video id
  default_url text,
  default_width int NOT NULL DEFAULT 0,
  default_height int NOT NULL DEFAULT 0,
  medium_url text,
  medium_width int NOT NULL DEFAULT 0,
  medium_height int NOT NULL DEFAULT 0,
  high_url text,
  high_width int NOT NULL DEFAULT 0,
  high_height int NOT NULL DEFAULT 0,
  standard_url text,
  standard_width int NOT NULL DEFAULT 0,
  standard_height int NOT NULL DEFAULT 0,
  maxres_url text,
  maxres_width int NOT NULL DEFAULT 0,
  maxres_height int NOT NULL DEFAULT 0,
  FOREIGN KEY(id) REFERENCES youtube_status_video(id),
  CONSTRAINT youtube_status_video_thumbnails_pkey PRIMARY KEY (id)
);
ALTER TABLE IF EXISTS public.youtube_status_video_thumbnails OWNER to webapp;
CREATE TABLE IF NOT EXISTS youtube_status_video_statistics (
  "timestamp" double precision NOT NULL DEFAULT EXTRACT(epoch FROM CURRENT_TIMESTAMP),
  id text NOT NULL, -- video id
  comment_count int NOT NULL DEFAULT 0, -- need str to int
  favorite_count int NOT NULL DEFAULT 0, -- need str to int
  like_count int NOT NULL DEFAULT 0, -- need str to int
  view_count int NOT NULL DEFAULT 0, -- need str to int
  FOREIGN KEY(id) REFERENCES youtube_status_video(id),
  CONSTRAINT youtube_status_video_statistics_pkey PRIMARY KEY (id)
);
ALTER TABLE IF EXISTS public.youtube_status_video_statistics OWNER to webapp;
CREATE OR REPLACE VIEW public.youtube_status_video_view
  AS
  SELECT 
    to_timestamp(trunc(public.youtube_status_video."timestamp")) as timestamp,
    public.youtube_status_video.id,
    public.youtube_status_video.category_id,
    public.youtube_status_channel.global_title as channel_title,
    public.youtube_status_video.default_audio_language,
    public.youtube_status_video.live_broadcast_content,
    public.youtube_status_video.published_at,
    public.youtube_status_video.global_title,
    public.youtube_status_video.global_description,
    public.youtube_status_video.localized_title,
    public.youtube_status_video.localized_description,
    public.youtube_status_video_statistics.comment_count,
    public.youtube_status_video_statistics.favorite_count,
    public.youtube_status_video_statistics.like_count,
    public.youtube_status_video_statistics.view_count
  FROM public.youtube_status_video
  JOIN public.youtube_status_channel
  ON public.youtube_status_video.channel_id=youtube_status_channel.id
  JOIN public.youtube_status_video_statistics
  ON public.youtube_status_video.id=youtube_status_video_statistics.id
  ORDER BY public.youtube_status_video."timestamp" DESC NULLS FIRST;
ALTER VIEW IF EXISTS public.youtube_status_video_view OWNER to webapp;
CREATE OR REPLACE VIEW public.youtube_status_channel_view
  AS
  SELECT 
    to_timestamp(trunc(public.youtube_status_channel."timestamp")) as timestamp,
    public.youtube_status_channel.id,
    public.youtube_status_channel.customUrl,
    public.youtube_status_channel.published_at,
    public.youtube_status_channel.global_title,
    public.youtube_status_channel.global_description,
    public.youtube_status_channel.localized_title,
    public.youtube_status_channel.localized_description,
    public.youtube_status_channel_statistics.hidden_subscriber_count,
    public.youtube_status_channel_statistics.subscriber_count,
    public.youtube_status_channel_statistics.video_count,
    public.youtube_status_channel_statistics.view_count
  FROM public.youtube_status_channel
  JOIN public.youtube_status_channel_statistics
  ON public.youtube_status_channel.id=youtube_status_channel_statistics.id
  ORDER BY public.youtube_status_channel."timestamp" DESC NULLS FIRST;
ALTER VIEW IF EXISTS public.youtube_status_channel_view OWNER to webapp;
