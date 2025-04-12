import { Metadata } from "next";
import ScrollUp from "@/components/Common/ScrollUp";
import RouteConfig from "@/components/RouteConfig/RouteConfig";

export const metadata: Metadata = {
  title: "PetWalk",
  description: "This is an app for pet lovers!",
  // other metadata
};

export default function Home() {
  return (
    <>
     <ScrollUp />
     <div className="flex min-h-[100vh] mt-[200px] px-6">
     {/* Lewa kolumna */}
     <div className="w-full md:w-1/3 flex flex-col items-start mt-[200px] gap-4">
     <RouteConfig />
     </div>

        {/* Prawa część (możesz dodać np. mapę, trasy itp.) */}
        <div className="w-full md:w-2/3 p-6">
          {/* Pozostała zawartość */}
      </div>
      </div>

    </>
  );
}