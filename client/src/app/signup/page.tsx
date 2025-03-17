import { Metadata } from "next";
import SignupForm from "../../components/Signup/signupForm";

export const metadata: Metadata = {
  title: "Sign Up Page",
};

export default function SignupPage() {
  return (
    <div>
      <SignupForm />
    </div>
  );
}