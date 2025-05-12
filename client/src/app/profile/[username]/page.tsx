"use client";
import { useParams } from "next/navigation";


export default function UserProfilePage() {
  const params = useParams();
  const username = params.username;

  return (
    <>
    <section className="min-h-[60vh] flex items-center justify-center text-center">
    <div>
    <h1 className="text-4xl font-bold mb-4"> </h1>

    <p className="text-lg opacity-0">costam</p>
    <p className="text-lg opacity-0">costam</p>
    <p className="text-lg opacity-0">costam</p>

    </div>
    </section>

    <div className="p-6 text-white">
      <h1 className="text-3xl font-bold">Profil użytkownika: {username}</h1>
      <p>Tu będzie więcej szczegółów o użytkowniku!</p>
    </div>
    </>
  );
}
