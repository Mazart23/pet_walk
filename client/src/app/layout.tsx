"use client";

import "animate.css";
import React from "react";
import Footer from "@/components/Footer";
import Header from "@/components/Header";
import { Providers } from "./providers";
import { ConfigProvider } from '../components/contexts/ConfigContext';
import { TokenProvider } from '../components/contexts/TokenContext';
import { WebsocketProvider } from "../components/contexts/WebsocketContext";
import { UserProvider } from "@/components/contexts/UserContext";
import ScrollToTop from "@/components/ScrollToTop";
import { Inter } from "next/font/google";
import "node_modules/react-modal-video/css/modal-video.css";
import "../styles/index.css";

const inter = Inter({ subsets: ["latin"] });

export const getColorFromUsername = (username: string | undefined): string => {
  if (!username) return "#33cc33";
  const hash = Array.from(username).reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const hue = hash % 360;
  return `hsl(${hue}, 70%, 50%)`;
};

export default function RootLayout({
  children,
} : {
  children: React.ReactNode;
}) {
  return (
    <html suppressHydrationWarning lang="en">
      {/*
        <head /> will contain the components returned by the nearest parent
        head.js. Find out more at https://beta.nextjs.org/docs/api-reference/file-conventions/head
      */}
      <head />

      <body className={`bg-[#FCFCFC] dark:bg-black ${inter.className}`}>
        <ConfigProvider>
          <TokenProvider>
            <WebsocketProvider>
              <UserProvider>
                <Providers>
                  <Header />
                  {children}
                  <Footer />
                  <ScrollToTop />
                </Providers>
              </UserProvider>
            </WebsocketProvider>
          </TokenProvider>
        </ConfigProvider>
      </body>
    </html>
  );
}

