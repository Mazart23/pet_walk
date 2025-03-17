"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Cookies from 'js-cookie';

const TokenContext = createContext();

const useToken = () => useContext(TokenContext);

export const TokenProvider = ({ children }) => {
  const [token, setToken] = useState(null);

  useEffect(() => {
    setToken(Cookies.get("token") || null);
  }, []);
  const router = useRouter();

  const saveToken = (newToken) => {
    Cookies.set("token", newToken);
    setToken(newToken);
  };

  const removeToken = () => {
    Cookies.remove("token");
    setToken(null);
    router.push("/about");
  };

  const contextValue = {
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
