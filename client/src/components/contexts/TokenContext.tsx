"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";

type TokenContextType = {
  token: string | null;
  setToken: (token: string) => void;
  removeToken: () => void;
};

const TokenContext = createContext<TokenContextType | undefined>(undefined);

const useToken = () => {
  const context = useContext(TokenContext);
  if (!context) {
    throw new Error("useToken must be used within a TokenProvider");
  }
  return context;
};

export const TokenProvider = ({ children }: { children: ReactNode }) => {
  const [token, setTokenState] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    setTokenState(Cookies.get("token") || null);
  }, []);

  const saveToken = (newToken: string) => {
    Cookies.set("token", newToken);
    setTokenState(newToken);
  };

  const removeToken = () => {
    Cookies.remove("token");
    setTokenState(null);
    router.push("/about");
  };

  const contextValue: TokenContextType = {
    token,
    setToken: saveToken,
    removeToken
  };

  return (
    <TokenContext.Provider value={contextValue}>
      {children}
    </TokenContext.Provider>
  );
};

export default useToken;
