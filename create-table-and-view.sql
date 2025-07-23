-- drop
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
  global_description text NOT NULL,
  localized_title text,
  localized_description text,
  CONSTRAINT youtube_status_channel_pkey PRIMARY KEY (id)
);
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
  global_description text NOT NULL,
  localized_title text,
  localized_description text,
  FOREIGN KEY(channel_id) REFERENCES youtube_status_channel(id),
  CONSTRAINT youtube_status_video_pkey PRIMARY KEY (id)
);
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
