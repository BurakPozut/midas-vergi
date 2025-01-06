"use server";

import { z } from "zod";
import { LoginSchema } from "@/schemas";
import { AuthError } from "next-auth";
// import { DEFAULT_LOGIN_REDIRECT } from "@/routes";
import { signIn } from "@/auth";
// import { redirect } from "next/navigation";

export async function login(values: z.infer<typeof LoginSchema>) {
  const validatedFields = LoginSchema.safeParse(values);
  if (!validatedFields.success) {
    return { success: "", error: "Invalid Credentials!" };
  }

  const { email, password } = validatedFields.data;
  //dummy wait 2 seconds
  // await new Promise((resolve) => setTimeout(resolve, 2000));
  try {
    const res = await signIn("credentials", {
      email,
      password,
      redirect: false,
      // redirectTo: DEFAULT_LOGIN_REDIRECT,
    });
    // Handle the response based on signIn result
    if (res?.error) {
      return { success: "", error: "Invalid Credentials!" };
    }

    // Successful login
    return { success: "logged in", error: "" };
  } catch (error) {
    if (error instanceof AuthError) {
      // const { type, cause } = error as AuthError;
      switch (error.type) {
        case "CredentialsSignin":
          return { success: "", error: "Invalid Credentials!" };
        default:
          return { success: "", error: "Something went wrong!" };
      }
    }
    console.error("Error in login Action: ", error);
    throw error;
  } finally {
    // redirect(DEFAULT_LOGIN_REDIRECT);
    // return { success: "logged in", error: "" };
  }
}
