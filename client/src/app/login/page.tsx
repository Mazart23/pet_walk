import { Metadata } from "next";
import LoginForm from "../../components/Login/loginForm";


export const metadata: Metadata = {
  title: "Sign In Page",
  // other metadata
};

export default function LoginPage() {
  return (
    <div>
      <LoginForm />
    </div>
  );
}
