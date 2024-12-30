"use server";

import { prisma } from "@/lib/prisma";
import { RegisterSchema } from "@/schemas";
import bcrypt from "bcryptjs";
import { z } from "zod";

type RegisterInput = z.infer<typeof RegisterSchema>;

export async function register(formData: RegisterInput) {
  const data = {
    email: formData.email,
    password: formData.password,
    name: formData.name,
  };

  console.log("Register action started with data:", {
    ...data,
    password: "***",
  });

  try {
    // Validate input with Zod
    const result = RegisterSchema.safeParse(data);
    if (!result.success) {
      console.error("Validation failed:", result.error);
      return { error: result.error.issues[0].message };
    }

    const { email, password, name } = result.data;

    // Check if user already exists
    const existingUser = await prisma.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      return { error: "Bu email adresi zaten kayıtlı" };
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        name,
      },
    });

    console.log("User created successfully:", {
      id: user.id,
      email: user.email,
    });

    return { success: true, user };
  } catch (error) {
    console.error("Registration error:", error);
    return { error: "Kayıt sırasında bir hata oluştu" };
  }
}
