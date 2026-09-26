'use client';

import { useEffect } from 'react';
import Script from 'next/script';

/**
 * Motor de Notificações Web Push (Via OneSignal / VAPID)
 * Este componente injeta o SDK do OneSignal e engatilha o Prompt de Inscrição 
 * após o usuário passar mais de 30 segundos no site.
 */
export default function PushNotification({ appId }: { appId?: string }) {
  useEffect(() => {
    if (!appId || typeof window === 'undefined') return;

    // Atrasar o pedido de permissão para não assustar o usuário
    const timer = setTimeout(() => {
      // @ts-ignore
      window.OneSignal = window.OneSignal || [];
      // @ts-ignore
      OneSignal.push(function () {
        // @ts-ignore
        OneSignal.init({
          appId: appId,
          safari_web_id: "web.onesignal.auto.safari",
          notifyButton: {
            enable: true,
            size: 'medium',
            theme: 'default',
            position: 'bottom-right',
            text: {
              'tip.state.unsubscribed': 'Assine para receber fofocas em primeira mão',
              'tip.state.subscribed': 'Você está inscrito!',
              'tip.state.blocked': 'Você bloqueou nossas notificações',
              'message.prenotify': 'Clique para assinar nossas notícias quentes',
              'message.action.subscribed': 'Obrigado por assinar!',
              'message.action.resubscribed': 'Você está inscrito novamente!',
              'message.action.unsubscribed': 'Você não receberá mais notícias de última hora',
            }
          },
          promptOptions: {
            slidedown: {
              prompts: [
                {
                  type: "push",
                  autoPrompt: true,
                  text: {
                    actionMessage: "Receba as fofocas e matérias de capa antes de todo mundo.",
                    acceptButton: "Permitir",
                    cancelButton: "Agora Não"
                  },
                  delay: {
                    pageViews: 1,
                    timeDelay: 15
                  }
                }
              ]
            }
          }
        });
      });
    }, 5000);

    return () => clearTimeout(timer);
  }, [appId]);

  if (!appId) return null;

  return (
    <Script
      src="https://cdn.onesignal.com/sdks/OneSignalSDK.js"
      strategy="afterInteractive"
    />
  );
}
