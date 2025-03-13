import { Dolar, PrismaClient, YiUfe } from "@prisma/client";
import * as fs from "fs";

const prisma = new PrismaClient();

async function main() {
  // Read JSON data
  const rawData = fs.readFileSync("prisma/Dolar.json", "utf8");
  const dolarData = JSON.parse(rawData);

  // Insert into Dolar table
  await prisma.dolar.createMany({
    data: dolarData.map((row: Dolar) => ({
      id: row.id,
      gecerliOlduguTarih: row.gecerliOlduguTarih,
      dovizAlis: row.dovizAlis,
    })),
    skipDuplicates: true, // Avoid duplicates if seeded multiple times
  });

  console.log("Seeded 750 rows into Dolar table");

  const rawDataYiUfe = fs.readFileSync("prisma/YiUfe.json", "utf8");
  const yiUfeData = JSON.parse(rawDataYiUfe);

  // Insert into YiUfe table
  await prisma.yiUfe.createMany({
    data: yiUfeData.map((row: YiUfe) => ({
      id: row.id,
      yil: row.yil,
      ocak: row.ocak,
      subat: row.subat,
      mart: row.mart,
      nisan: row.nisan,
      mayis: row.mayis,
      haziran: row.haziran,
      temmuz: row.temmuz,
      agustos: row.agustos,
      eylul: row.eylul,
      ekim: row.ekim,
      kasim: row.kasim,
      aralik: row.aralik,
    })),
    skipDuplicates: true, // Avoid duplicates if seeded multiple times
  });

  console.log("Seeded 12 rows into YiUfe table");
}

main()
  .catch((e) => console.error(e))
  .finally(async () => await prisma.$disconnect());
