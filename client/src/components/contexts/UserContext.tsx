import React, { createContext, useContext, useState, useEffect } from "react";
import useToken from "./TokenContext";
import useWebsocket from "./WebsocketContext";
import { fetchUserSelfData } from "@/app/Api";

const UserContext = createContext();

const useUser = () => useContext(UserContext);

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const { token } = useToken();
  const { socket } = useWebsocket();

  useEffect(() => {
    if (token && socket) {
      fetchUserSelfData(token).then((data) => {
        setUser(data);
      })
    } else {
      setUser(null);
    }
  }, [token, socket]);

  const contextValue = {
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