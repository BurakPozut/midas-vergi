import { auth } from "@/auth";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const isOnDashboard = req.nextUrl.pathname.startsWith("/dashboard");
  const isOnProfile = req.nextUrl.pathname.startsWith("/profile");
  const isOnUpload = req.nextUrl.pathname.startsWith("/upload");

  if (!isLoggedIn && (isOnDashboard || isOnProfile || isOnUpload)) {
    return Response.redirect(new URL("/api/auth/signin", req.url));
  }
});

// Optionally configure middleware
export const config = {
  matcher: ["/dashboard/:path*", "/profile/:path*", "/upload/:path*"],
};
