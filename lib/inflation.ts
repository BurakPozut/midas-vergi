import { db } from "./prisma";

const MONTH_FIELDS = [
  "ocak",
  "subat",
  "mart",
  "nisan",
  "mayis",
  "haziran",
  "temmuz",
  "agustos",
  "eylul",
  "ekim",
  "kasim",
  "aralik",
] as const;

export async function getInflationRate(
  buyYear: number,
  buyMonth: number,
  sellYear: number,
  sellMonth: number
): Promise<number | null> {
  try {
    // Get all relevant years
    const rates = await db.yiUfe.findMany({
      where: {
        yil: {
          gte: buyYear,
          lte: sellYear,
        },
      },
      orderBy: {
        yil: "asc",
      },
    });

    if (!rates.length) {
      return null;
    }

    // Calculate inflation rate
    let startValue: number | null = null;
    let endValue: number | null = null;

    // Find start value
    const startYear = rates.find((r) => r.yil === buyYear);
    if (startYear) {
      startValue = startYear[MONTH_FIELDS[buyMonth]];
    }

    // Find end value
    const endYear = rates.find((r) => r.yil === sellYear);
    if (endYear) {
      endValue = endYear[MONTH_FIELDS[sellMonth]];
    }

    if (startValue === null || endValue === null) {
      return null;
    }

    // Calculate percentage change
    const inflationRate = ((endValue - startValue) / startValue) * 100;
    return inflationRate;
  } catch (error) {
    console.error("Error calculating inflation rate:", error);
    return null;
  }
}
