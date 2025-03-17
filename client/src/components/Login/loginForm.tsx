"use client";

import React, { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import useToken from "../contexts/TokenContext";
import { postLogin } from "../../app/Api";

const LoginForm = () => {
  const router = useRouter();
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [errors, setErrors] = useState({ general: "" });
  const { setToken } = useToken();

  const handleInputChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }, []);

  const handleLogin = useCallback(
    async (e) => {
      e.preventDefault();
      setErrors({ general: "" });

      try {
        const accessToken = await postLogin(formData.username, formData.password);
        setToken(accessToken);
        router.push("/");
      } catch {
        setErrors({ general: "Password or username is incorrect." });
      }
    },
    [formData, router, setToken]
  );

  return (
    <section className="relative z-10 overflow-hidden pb-16 pt-36 md:pb-20 lg:pb-28 lg:pt-[180px]">
      <div className="container">
        <div className="-mx-4 flex flex-wrap">
          <div className="w-full px-4">
            <div className="shadow-three mx-auto max-w-[500px] rounded bg-white px-6 py-10 dark:bg-dark sm:p-[60px]">
              <h3 className="mb-3 text-center text-2xl font-bold text-black dark:text-white sm:text-3xl">
                Sign in to your account
              </h3>
              <form onSubmit={handleLogin}>
                <div className="mb-8">
                  <label htmlFor="username" className="mb-3 block text-sm text-dark dark:text-white">
                    Your Username
                  </label>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    placeholder="Enter your username"
                    value={formData.username}
                    onChange={handleInputChange}
                    className="w-full rounded-sm border border-stroke bg-[#f8f8f8] px-6 py-3 text-base text-body-color outline-none transition-all duration-300 focus:border-primary dark:border-transparent dark:bg-[#2C303B] dark:text-body-color-dark dark:shadow-two dark:focus:border-primary dark:focus:shadow-none"
                  />
                </div>
                <div className="mb-8">
                  <label htmlFor="password" className="mb-3 block text-sm text-dark dark:text-white">
                    Your Password
                  </label>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    placeholder="Enter your Password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className="w-full rounded-sm border border-stroke bg-[#f8f8f8] px-6 py-3 text-base text-body-color outline-none transition-all duration-300 focus:border-primary dark:border-transparent dark:bg-[#2C303B] dark:text-body-color-dark dark:shadow-two dark:focus:border-primary dark:focus:shadow-none"
                  />
                </div>
                {errors.general && (
                  <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-md">
                    <p className="text-red-500 text-center text-sm">{errors.general}</p>
                  </div>
                )}
                <div className="mb-6">
                  <button
                    type="submit"
                    className="flex w-full items-center justify-center rounded-sm bg-green-500 px-9 py-4 text-base font-medium text-white shadow-submit duration-300 hover:bg-green-600 dark:shadow-submit-dark"
                  >
                    Sign in
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default LoginForm;