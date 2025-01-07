import { db } from "./prisma";

export async function getDolarRate(date: Date): Promise<number | null> {
  const formattedDate = date.toLocaleDateString("tr-TR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });

  // console.log("Getting dolar rate for date:", formattedDate);
  // Try to get from database first
  const rate = await db.dolar.findFirst({
    where: {
      gecerliOlduguTarih: formattedDate,
    },
  });
  // console.log("Rate:", rate);
  if (rate) {
    return rate.dovizAlis;
  }

  // If not in database, return null
  return null;
}
