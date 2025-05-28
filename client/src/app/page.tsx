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
      <section className=" flex items-center justify-center text-center">
        <div>
          <h1 className="text-4xl font-bold mb-4"> </h1>

          <p className="text-lg opacity-0">costam</p>

        </div>
      </section>
      <section className=" py-10 px-6">
        <RouteConfig />
      </section>
    </>
  );
}

