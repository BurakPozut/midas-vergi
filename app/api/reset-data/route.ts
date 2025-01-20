import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { db } from "@/lib/prisma";

export async function POST() {
  try {
    const session = await auth();
    const userId = session?.user?.id;

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Delete all transactions and dividends for the user
    await Promise.all([
      db.transaction.deleteMany({
        where: {
          userId: userId,
        },
      }),
      db.dividend.deleteMany({
        where: {
          userId: userId,
        },
      }),
    ]);

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Error resetting data:", error);
    return NextResponse.json(
      { error: "Error resetting user data" },
      { status: 500 }
    );
  }
}
