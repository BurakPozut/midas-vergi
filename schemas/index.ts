import * as z from "zod";

export const RegisterSchema = z.object({
  email: z.string().email("Geçerli bir email adresi giriniz"),
  password: z.string().min(8, "Şifre en az 8 karakter olmalıdır"),
  name: z.string().min(1, "Ad Soyad alanı zorunludur"),
});

export const LoginSchema = z.object({
  email: z.string().email({ message: "Geçerli bir email adresi girin" }),
  password: z.string().min(1, { message: "Şifre gerekli" }),
});
