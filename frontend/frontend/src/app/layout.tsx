import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";
import PushNotification from "@/components/PushNotification";
import GlobalTooltip from "@/components/ui/GlobalTooltip";
import { ToastContainer } from "@/components/ui/Toast";
import ContextMenu from "@/components/ui/ContextMenu";
import BackgroundParticles from "@/components/ui/BackgroundParticles";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Auto-Blog CMS | O Futuro da Mídia",
  description: "Fábrica autônoma de conteúdo guiada por Inteligência Artificial.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className={`${inter.variable} ${outfit.variable} antialiased relative min-h-screen`}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem disableTransitionOnChange>
          {/* Efeito de luz de fundo e Partículas */}
          <div className="bg-glow"></div>
          <BackgroundParticles />
          
          {children}
          
          <GlobalTooltip />
          <ToastContainer />
          <ContextMenu />

          {/* Motor de Notificação Push (OneSignal) */}
          <PushNotification appId={process.env.NEXT_PUBLIC_ONESIGNAL_ID} />
          
          {/* Honey Pot (Ratoeira para Bot de Scraping) */}
          <a href="/api/trap" className="absolute top-0 left-0 w-0 h-0 opacity-0 pointer-events-none -z-50 select-none" aria-hidden="true" tabIndex={-1} rel="nofollow">
            Area VIP Secreta
          </a>
        </ThemeProvider>
      </body>
    </html>
  );
}
