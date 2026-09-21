'use client';

import React from 'react';
import AudioPlayerBlock from './AudioPlayerBlock';
import VideoSeriesBlock from './VideoSeriesBlock';
import PhotoGalleryBlock from './PhotoGalleryBlock';
import NewsTimelineBlock from './NewsTimelineBlock';

export interface InteractiveMediaProps {
  postType?: string;
  mediaPayload?: string | Record<string, any>;
  primaryColor?: string;
  secondaryColor?: string;
  accentStyle?: string;
}

export default function InteractiveMediaRouter({
  postType = 'article',
  mediaPayload,
  primaryColor = '#06b6d4',
  secondaryColor = '#3b82f6',
  accentStyle = 'rounded'
}: InteractiveMediaProps) {
  if (!postType || postType === 'article') {
    // Se for article normal mas tiver um mediaPayload com dados, tenta adivinhar o tipo!
    if (!mediaPayload || mediaPayload === '{}' || mediaPayload === '') return null;
  }

  let payloadObj: Record<string, any> = {};
  try {
    if (typeof mediaPayload === 'string') {
      payloadObj = JSON.parse(mediaPayload || '{}');
    } else if (typeof mediaPayload === 'object' && mediaPayload !== null) {
      payloadObj = mediaPayload;
    }
  } catch (e) {
    payloadObj = {};
  }

  // Determinar qual componente renderizar
  switch (postType) {
    case 'audio_track':
      return (
        <AudioPlayerBlock
          payload={payloadObj}
          primaryColor={primaryColor}
          secondaryColor={secondaryColor}
          accentStyle={accentStyle}
        />
      );
    case 'video_series':
      return (
        <VideoSeriesBlock
          payload={payloadObj}
          primaryColor={primaryColor}
          secondaryColor={secondaryColor}
          accentStyle={accentStyle}
        />
      );
    case 'photo_gallery':
      return (
        <PhotoGalleryBlock
          payload={payloadObj}
          primaryColor={primaryColor}
          secondaryColor={secondaryColor}
          accentStyle={accentStyle}
        />
      );
    case 'news_timeline':
      return (
        <NewsTimelineBlock
          payload={payloadObj}
          primaryColor={primaryColor}
          secondaryColor={secondaryColor}
          accentStyle={accentStyle}
        />
      );
    default:
      return null;
  }
}
