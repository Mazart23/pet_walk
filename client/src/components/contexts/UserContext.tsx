import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import useToken from "./TokenContext";
import useWebsocket from "./WebsocketContext";
import { fetchUserSelfData } from "@/app/Api";

// 1. Typ danych użytkownika (dopasuj do zwracanej struktury z fetchUserSelfData)
type User = {
  id: number;
  username: string;
  email: string;
  profile_picture_url?: string;
  // dodaj inne pola jeśli są
};

// 2. Typ kontekstu
type UserContextType = {
  userSelf: User | null;
  setUserSelf: React.Dispatch<React.SetStateAction<User | null>>;
};

// 3. Tworzenie kontekstu
const UserContext = createContext<UserContextType | undefined>(undefined);

// 4. Hook z walidacją
const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
};

// 5. Provider z typami propsów
export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const { token } = useToken();
  const { socket } = useWebsocket();

  useEffect(() => {
    if (token && socket) {
      fetchUserSelfData(token).then((data) => {
        setUser(data);
      });
    } else {
      setUser(null);
    }
  }, [token, socket]);

  const contextValue: UserContextType = {
    userSelf: user,
    setUserSelf: setUser
  };

  return (
    <UserContext.Provider value={contextValue}>
      {children}
    </UserContext.Provider>
  );
};

export default useUser;
