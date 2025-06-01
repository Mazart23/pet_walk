"use client";

import React from "react";
import Header from "./Header";
import Footer from "./Footer";
import { Providers } from "@/app/providers";
import { ConfigProvider } from "./contexts/ConfigContext";
import { TokenProvider } from "./contexts/TokenContext";
import { WebsocketProvider } from "./contexts/WebsocketContext";
import { UserProvider } from "./contexts/UserContext";
import ToastWrapper from "./ToastWrapper";
import LeafletInit from "./LeafletInit";
import ScrollToTop from "./ScrollToTop";


export default function LayoutClientShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <LeafletInit />
      <ToastWrapper />
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
    </>
  );
}
