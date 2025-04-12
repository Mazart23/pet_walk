"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";

// 1. Typ kontekstu
type TokenContextType = {
  token: string | null;
  setToken: (token: string) => void;
  removeToken: () => void;
};

// 2. Domyślnie undefined
const TokenContext = createContext<TokenContextType | undefined>(undefined);

// 3. Hook z walidacją
const useToken = () => {
  const context = useContext(TokenContext);
  if (!context) {
    throw new Error("useToken must be used within a TokenProvider");
  }
  return context;
};

// 4. Provider z typami propsów
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
