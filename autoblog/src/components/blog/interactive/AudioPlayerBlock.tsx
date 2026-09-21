'use client';

import React, { useState, useEffect, useRef } from 'react';

export interface AudioTrackData {
  title: string;
  artist: string;
  url?: string;
  duration?: string;
  coverUrl?: string;
  genre?: string;
}

interface AudioPlayerBlockProps {
  payload: {
    track?: AudioTrackData;
    playlist?: AudioTrackData[];
  };
  primaryColor?: string;
  secondaryColor?: string;
  accentStyle?: string;
}

export default function AudioPlayerBlock({
  payload,
  primaryColor = '#a855f7',
  secondaryColor = '#ec4899',
  accentStyle = 'rounded'
}: AudioPlayerBlockProps) {
  const tracks: AudioTrackData[] = payload.playlist || (payload.track ? [payload.track] : [
    {
      title: 'Synthwave Nightfall (Faixa IA)',
      artist: 'Redação Neural • Dark Trap Radio',
      duration: '3:45',
      genre: 'Phonk / Dark Trap',
      url: 'https://cdn.pixabay.com/download/audio/2022/05/16/audio_db6591201e.mp3?filename=cyberpunk-city-110296.mp3'
    },
    {
      title: 'Neon Drift 2026 (Instrumental)',
      artist: 'Redação Neural • Beats Autônomos',
      duration: '4:12',
      genre: 'Cyberpunk Synth',
      url: 'https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=synthwave-80s-110045.mp3'
    }
  ]);

  const [currentIdx, setCurrentIdx] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTime, setCurrentTime] = useState('0:00');
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const currentTrack = tracks[currentIdx] || tracks[0];

  const radiusMap: Record<string, string> = {
    sharp: '0px',
    rounded: '16px',
    pill: '28px'
  };
  const radius = radiusMap[accentStyle] || '16px';
  const pillRadius = accentStyle === 'sharp' ? '0px' : '9999px';

  useEffect(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio(currentTrack.url);
    } else {
      audioRef.current.src = currentTrack.url || '';
    }

    const audio = audioRef.current;
    
    const updateTime = () => {
      if (audio.duration) {
        const pct = (audio.currentTime / audio.duration) * 100;
        setProgress(pct);
        const mins = Math.floor(audio.currentTime / 60);
        const secs = Math.floor(audio.currentTime % 60);
        setCurrentTime(`${mins}:${secs < 10 ? '0' : ''}${secs}`);
      }
    };

    const handleEnded = () => {
      if (currentIdx < tracks.length - 1) {
        setCurrentIdx(prev => prev + 1);
      } else {
        setIsPlaying(false);
        setProgress(0);
      }
    };

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('ended', handleEnded);

    if (isPlaying) {
      audio.play().catch(() => setIsPlaying(false));
    }

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('ended', handleEnded);
      audio.pause();
    };
  }, [currentIdx, currentTrack.url]);

  const [activeTab, setActiveTab] = useState<'stream' | 'podcast'>('stream');
  const [podcastLoading, setPodcastLoading] = useState(false);
  const [podcastData, setPodcastData] = useState<any>(null);
  const [activeSpeakerIdx, setActiveSpeakerIdx] = useState<number | null>(null);
  const [podcastPlaying, setPodcastPlaying] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 4000);
  };

  const handleGeneratePodcast = async () => {
    setPodcastLoading(true);
    showToast("⚡ Sintetizar roteiro de entrevista AI (Aoede & Charon)...");
    try {
      const res = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: 'dual_host',
          title: currentTrack.title,
          text: currentTrack.artist,
          niche: currentTrack.genre || 'Tecnologia'
        })
      });
      const data = await res.json();
      if (data.success && data.podcast) {
        setPodcastData(data.podcast);
        showToast("🎙️ Entrevista Dual-Host gerada com sucesso! Clique para reproduzir.");
      } else {
        showToast("⚠️ Erro ao gerar podcast. Tente novamente.");
      }
    } catch (e) {
      showToast("❌ Falha de conexão ao gerar podcast.");
    } finally {
      setPodcastLoading(false);
    }
  };

  useEffect(() => {
    let timer: any;
    if (podcastPlaying && podcastData?.dialogue) {
      let idx = 0;
      setActiveSpeakerIdx(0);
      timer = setInterval(() => {
        idx++;
        if (idx < podcastData.dialogue.length) {
          setActiveSpeakerIdx(idx);
        } else {
          setPodcastPlaying(false);
          setActiveSpeakerIdx(null);
          showToast("🏁 Fim do episódio do podcast!");
          clearInterval(timer);
        }
      }, 5000); // 5s por turno de fala
    }
    return () => clearInterval(timer);
  }, [podcastPlaying, podcastData]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(false));
    }
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!audioRef.current || !audioRef.current.duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const width = rect.width;
    const pct = clickX / width;
    audioRef.current.currentTime = pct * audioRef.current.duration;
    setProgress(pct * 100);
  };

  return (
    <div 
      className="my-8 p-6 md:p-8 bg-slate-900/90 border-2 shadow-2xl backdrop-blur-xl relative overflow-hidden transition-all duration-300"
      style={{
        borderColor: `${primaryColor}50`,
        borderRadius: radius,
        boxShadow: `0 10px 30px -10px ${primaryColor}25`
      }}
    >
      {/* Toast Comemorativo Zero Dialogs */}
      {toast && (
        <div className="absolute top-4 right-4 z-50 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-xs font-bold px-4 py-2 rounded-xl shadow-2xl animate-bounce flex items-center gap-2 border border-white/20">
          <span>🔔</span> {toast}
        </div>
      )}

      {/* Glow de fundo */}
      <div 
        className="absolute -top-24 -right-24 w-64 h-64 rounded-full blur-3xl opacity-20 pointer-events-none transition-all duration-700"
        style={{ backgroundColor: isPlaying || podcastPlaying ? primaryColor : secondaryColor }}
      />

      {/* Seletor de Abas Executivo */}
      <div className="flex flex-wrap items-center justify-between mb-6 relative z-10 border-b border-slate-800 pb-4 gap-3">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full animate-ping" style={{ backgroundColor: primaryColor }} />
          <span className="text-xs font-black uppercase tracking-widest" style={{ color: primaryColor }}>
            🎧 Módulo de Áudio & Podcast AI
          </span>
        </div>
        <div className="flex bg-slate-950/80 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => {
              setActiveTab('stream');
              setPodcastPlaying(false);
            }}
            className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all ${
              activeTab === 'stream' ? 'bg-purple-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            🎵 Áudio Stream
          </button>
          <button
            onClick={() => {
              setActiveTab('podcast');
              if (isPlaying) togglePlay();
              if (!podcastData) handleGeneratePodcast();
            }}
            className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-all flex items-center gap-1.5 ${
              activeTab === 'podcast' ? 'bg-gradient-to-r from-pink-600 to-purple-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            🎙️ Podcast Dual-Host AI
          </button>
        </div>
      </div>

      {activeTab === 'stream' ? (
        <>
          {/* Main Track Info & Controls */}
          <div className="flex flex-col md:flex-row items-center gap-6 relative z-10 mb-6">
            <button
              onClick={togglePlay}
              className="w-16 h-16 md:w-20 md:h-20 shrink-0 flex items-center justify-center text-white text-2xl md:text-3xl shadow-2xl transition-all hover:scale-105 active:scale-95 cursor-pointer border-2 border-white/20"
              style={{
                background: `linear-gradient(135deg, ${primaryColor}, ${secondaryColor})`,
                borderRadius: pillRadius,
                boxShadow: `0 0 25px ${primaryColor}60`
              }}
              title={isPlaying ? 'Pausar' : 'Reproduzir'}
            >
              {isPlaying ? '⏸' : '▶'}
            </button>

            <div className="flex-1 min-w-0 w-full text-center md:text-left">
              <h3 className="text-lg md:text-xl font-black text-white truncate leading-snug mb-1">
                {currentTrack.title}
              </h3>
              <p className="text-xs text-slate-400 font-medium truncate mb-4">
                {currentTrack.artist}
              </p>

              <div className="flex items-end justify-center md:justify-start gap-1 h-8 mb-2">
                {[40, 70, 30, 90, 60, 100, 50, 80, 40, 60, 90, 30, 70, 50, 80, 60, 40, 90, 70, 30, 80, 50, 60, 40].map((h, i) => (
                  <div
                    key={i}
                    className="w-1.5 transition-all duration-150 rounded-full"
                    style={{
                      height: isPlaying ? `${Math.max(15, (h * ((i % 3) + 1) * Math.random()))}%` : `${h * 0.3}%`,
                      backgroundColor: i / 24 < progress / 100 ? primaryColor : '#334155',
                      opacity: isPlaying ? 0.9 : 0.4
                    }}
                  />
                ))}
              </div>

              <div 
                onClick={handleSeek}
                className="w-full h-2 bg-slate-800 rounded-full cursor-pointer relative overflow-hidden group"
              >
                <div 
                  className="h-full transition-all duration-100 rounded-full"
                  style={{
                    width: `${progress}%`,
                    background: `linear-gradient(90deg, ${primaryColor}, ${secondaryColor})`
                  }}
                />
              </div>
              <div className="flex justify-between items-center text-[10px] font-mono text-slate-500 mt-1">
                <span>{currentTime}</span>
                <span>{currentTrack.duration || '3:45'}</span>
              </div>
            </div>
          </div>

          {tracks.length > 1 && (
            <div className="mt-6 pt-4 border-t border-slate-800/80 relative z-10">
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-3">
                📋 Playlist Editorial ({tracks.length} faixas)
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {tracks.map((t, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setCurrentIdx(idx);
                      setIsPlaying(true);
                    }}
                    className={`p-3 border text-left transition-all flex items-center justify-between group ${
                      currentIdx === idx ? 'bg-slate-800/90 text-white shadow-md border-opacity-80' : 'bg-slate-950/40 border-slate-800/60 text-slate-400 hover:text-white hover:bg-slate-800/40'
                    }`}
                    style={{
                      borderRadius: radius,
                      borderColor: currentIdx === idx ? primaryColor : undefined
                    }}
                  >
                    <div className="min-w-0 flex-1 pr-2">
                      <div className="text-xs font-bold truncate group-hover:text-white">
                        {idx + 1}. {t.title}
                      </div>
                      <div className="text-[10px] text-slate-500 truncate">{t.artist}</div>
                    </div>
                    {currentIdx === idx && isPlaying ? (
                      <span className="text-xs animate-bounce" style={{ color: primaryColor }}>ılılı</span>
                    ) : (
                      <span className="text-xs opacity-40 group-hover:opacity-100">▶</span>
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        /* ABA 2: ESTÚDIO PODCAST DUAL-HOST (MESA DE SOM VIRTUAL) */
        <div className="relative z-10 space-y-6">
          {podcastLoading ? (
            <div className="py-16 text-center space-y-4">
              <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-xs font-mono text-purple-300 animate-pulse">
                🧠 Sintetizando roteiro de entrevista AI com locutores virtuais Aoede & Charon...
              </p>
            </div>
          ) : !podcastData ? (
            <div className="py-12 text-center bg-slate-950/60 rounded-2xl border border-slate-800 p-6 space-y-4">
              <p className="text-sm text-slate-300 font-medium">
                Deseja transformar este artigo em uma **Entrevista de Rádio/Podcast** entre 2 locutores virtuais?
              </p>
              <button
                onClick={handleGeneratePodcast}
                className="px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold text-xs shadow-lg hover:scale-105 transition-all"
              >
                🎙️ Gerar Podcast Entrevista AI
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Cabeçalho do Episódio */}
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-950/80 p-4 rounded-2xl border border-purple-500/30 gap-4">
                <div>
                  <span className="text-[10px] font-mono text-pink-400 font-bold uppercase tracking-wider block">
                    {podcastData.episodeName || 'EP. #01 • Especial Neural'}
                  </span>
                  <h4 className="text-base md:text-lg font-black text-white">
                    {podcastData.podcastTitle || currentTrack.title}
                  </h4>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => {
                      setPodcastPlaying(!podcastPlaying);
                      if (!podcastPlaying) showToast("▶️ Reproduzindo Entrevista ao Vivo!");
                    }}
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white font-bold text-xs shadow-lg transition-all flex items-center gap-2"
                  >
                    <span>{podcastPlaying ? '⏸' : '▶'}</span>
                    <span>{podcastPlaying ? 'Pausar Entrevista' : 'Tocar Entrevista'}</span>
                  </button>
                </div>
              </div>

              {/* Mesa de Som / Avatares dos Hosts */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {(podcastData.hosts || [
                  { name: 'Aoede', role: 'Host & Apresentadora', avatar: '🎙️', color: '#a855f7' },
                  { name: 'Charon', role: 'Especialista Neural', avatar: '🎧', color: '#06b6d4' }
                ]).map((host: any, idx: number) => {
                  const isTalking = podcastPlaying && (
                    (activeSpeakerIdx !== null && podcastData?.dialogue?.[activeSpeakerIdx]?.speaker?.includes(host.name)) ||
                    (activeSpeakerIdx === null && idx === 0)
                  );
                  return (
                    <div
                      key={idx}
                      className={`p-4 rounded-2xl border transition-all flex items-center gap-4 ${
                        isTalking
                          ? 'bg-purple-950/60 border-purple-400 shadow-xl scale-102 ring-2 ring-purple-500/50'
                          : 'bg-slate-950/60 border-slate-800/80 opacity-75'
                      }`}
                    >
                      <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-700 flex items-center justify-center text-2xl shadow-inner shrink-0">
                        {host.avatar || '🎙️'}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between">
                          <h5 className="text-sm font-bold text-white truncate">{host.name}</h5>
                          {isTalking && (
                            <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-purple-500 text-white animate-pulse">
                              AO VIVO 🔴
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-400 truncate">{host.role}</p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Teleprompter / Legenda do Diálogo em Tempo Real */}
              <div className="bg-slate-950/90 rounded-2xl border border-slate-800/80 p-5 space-y-3 max-h-64 overflow-y-auto">
                <div className="text-[10px] font-mono text-slate-400 uppercase tracking-wider mb-2 flex justify-between items-center">
                  <span>📜 Transcrição Ao Vivo (Teleprompter)</span>
                  <span className="text-purple-400">{podcastData?.dialogue?.length || 0} turnos</span>
                </div>
                {(podcastData?.dialogue || []).map((turn: any, idx: number) => {
                  const isCurrent = activeSpeakerIdx === idx;
                  return (
                    <div
                      key={idx}
                      className={`p-3 rounded-xl transition-all border ${
                        isCurrent
                          ? 'bg-purple-900/40 border-purple-500/60 text-white shadow-md translate-x-1'
                          : 'bg-slate-900/40 border-transparent text-slate-400 hover:bg-slate-900/60'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs font-black ${isCurrent ? 'text-purple-300' : 'text-slate-500'}`}>
                          {turn.speaker}:
                        </span>
                      </div>
                      <p className="text-xs leading-relaxed font-sans">{turn.text}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
