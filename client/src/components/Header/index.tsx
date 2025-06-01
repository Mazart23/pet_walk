"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import ThemeToggler from "./ThemeToggler";
import useToken from "../contexts/TokenContext";
import useUser from "../contexts/UserContext";
import { SiDatadog } from "react-icons/si";
import { ArrowBigRightDash } from 'lucide-react';
import { getColorFromUsername } from "@/app/layout";

const Header = () => {
  // Token state
  const { token, removeToken } = useToken();
  const { userSelf } = useUser();

  // Navbar toggle
  const [navbarOpen, setNavbarOpen] = useState(false);
  const [sticky, setSticky] = useState(false);
  const navbarToggleHandler = () => {
    setNavbarOpen(!navbarOpen);
  };

  // Sticky Navbar
  useEffect(() => {
    const handleStickyNavbar = () => {
      if (window.scrollY >= 80) {
        setSticky(true);
      } else {
        setSticky(false);
      }
    };
  
    window.addEventListener("scroll", handleStickyNavbar);
    return () => {
      window.removeEventListener("scroll", handleStickyNavbar);
    };
  }, []);
  

  // submenu handler
  const [openIndex, setOpenIndex] = useState(-1);
  const handleSubmenu = (index) => {
    if (openIndex === index) {
      setOpenIndex(-1);
    } else {
      setOpenIndex(index);
    }
  };

  const usePathName = usePathname();

  const handleLogout = (() => {
    removeToken();
  });

  return (
    <>
      <header
        className={`header left-0 top-0 z-40 flex w-full items-center h-[96px] ${
          sticky
            ? "dark:bg-gray-dark dark:shadow-sticky-dark fixed z-[9999] bg-white !bg-opacity-80 shadow-sticky backdrop-blur-sm transition"
            : "absolute bg-transparent"
        }`}
      >
        <div className="container">
          <div className="relative -mx-4 flex items-center justify-between">
            <div className="w-60 max-w-full px-4 xl:mr-12">
              <Link
                href="/"
                className={`header-logo block w-full ${
                  sticky ? "py-5 lg:py-2" : "py-8"
                } `}
              >
                <Image
                  src="/images/logo/logo.png"
                  alt="logo"
                  width={60}
                  height={60}
                  className="w-[80px]"
                />
              </Link>
            </div>
            <div className="flex w-full items-center justify-end px-4">
              <div className="flex items-center gap-4">
                <ThemeToggler />
                {token ? (
                  <>
                    <Link
                      href="/"
                      onClick={handleLogout}
                      className="px-7 py-3 text-base font-medium text-dark hover:opacity-70 dark:text-white"
                    >
                      Logout
                    </Link>
                    <span className="text-base font-medium text-dark opacity-70 dark:text-white">
                      Routes
                    </span>
                    <ArrowBigRightDash className="text-base font-medium text-dark opacity-70 dark:text-white" />
                    <div className={`h-12 w-12 relative ${userSelf?.profile_picture_url !== undefined ? "animate__animated animate__fadeInTop" : ""}`}>
                    {userSelf && userSelf?.profile_picture_url !== undefined && 
                      <Link href={`/profile/${userSelf?.username}`}>
                          { userSelf?.profile_picture_url === "" ? (
                            <SiDatadog 
                              className="h-full w-full rounded-full object-cover transition-all duration-300 ease-in-out hover:scale-110 cursor-pointer border-2 border-solid border-indigo-900 shadow-md hover:shadow-lg shadow-indigo-900" 
                              style={{
                                color: getColorFromUsername(userSelf?.username),
                              }}
                            />
                          ):(
                            <Image
                              src={userSelf?.profile_picture_url}
                              fill
                              alt="User profile picture"
                              className="h-full w-full rounded-full object-cover transition-all duration-300 ease-in-out hover:scale-110 cursor-pointer border-2 border-solid border-indigo-900 shadow-md hover:shadow-lg shadow-indigo-900"
                            />
                          )}
                      </Link>
                    }
                    </div>
                  </>
                ):(
                  <>
                    <Link
                      href="/login"
                      className="px-7 py-3 text-base font-medium text-dark hover:opacity-70 dark:text-white"
                    >
                      Sign In
                    </Link>
                    <Link
                      href="/signup"
                      className="ease-in-up shadow-btn hover:shadow-btn-hover rounded-sm bg-sky-500 px-8 py-3 text-base font-medium text-white transition duration-300 hover:bg-sky-600 md:block md:px-9 lg:px-6 xl:px-9"
                    >
                      Sign Up
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>
    </>
  );
};

export default Header;
