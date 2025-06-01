import { Metadata } from "next";
import ScrollUp from "@/components/Common/ScrollUp";
import RouteConfig from "@/components/RouteConfig/RouteConfig";

export const metadata: Metadata = {
  title: "PetWalk",
  description: "This is an app for pet lovers!",
};

export default function Home() {
  return (
    <>
      <ScrollUp />
      <section className=" pt-24 px-6">
        <RouteConfig />
      </section>
    </>
  );
}

