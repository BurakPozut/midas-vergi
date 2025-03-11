-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "password" TEXT NOT NULL,
    "name" TEXT,
    "usage" INTEGER NOT NULL DEFAULT 3,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Transaction" (
    "id" SERIAL NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "transactionType" TEXT NOT NULL,
    "symbol" TEXT NOT NULL,
    "operationType" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "currency" TEXT NOT NULL,
    "orderQuantity" DOUBLE PRECISION NOT NULL,
    "orderAmount" DOUBLE PRECISION NOT NULL,
    "executedQuantity" DOUBLE PRECISION NOT NULL,
    "averagePrice" DOUBLE PRECISION NOT NULL,
    "transactionFee" DOUBLE PRECISION NOT NULL,
    "transactionAmount" DOUBLE PRECISION NOT NULL,
    "userId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Transaction_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Dolar" (
    "id" SERIAL NOT NULL,
    "gecerliOlduguTarih" TEXT NOT NULL,
    "dovizAlis" DOUBLE PRECISION NOT NULL,

    CONSTRAINT "Dolar_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "YiUfe" (
    "id" SERIAL NOT NULL,
    "yil" INTEGER NOT NULL,
    "ocak" DOUBLE PRECISION NOT NULL,
    "subat" DOUBLE PRECISION NOT NULL,
    "mart" DOUBLE PRECISION NOT NULL,
    "nisan" DOUBLE PRECISION NOT NULL,
    "mayis" DOUBLE PRECISION NOT NULL,
    "haziran" DOUBLE PRECISION NOT NULL,
    "temmuz" DOUBLE PRECISION NOT NULL,
    "agustos" DOUBLE PRECISION NOT NULL,
    "eylul" DOUBLE PRECISION NOT NULL,
    "ekim" DOUBLE PRECISION NOT NULL,
    "kasim" DOUBLE PRECISION NOT NULL,
    "aralik" DOUBLE PRECISION,

    CONSTRAINT "YiUfe_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Dividend" (
    "id" SERIAL NOT NULL,
    "paymentDate" TIMESTAMP(3) NOT NULL,
    "symbol" TEXT NOT NULL,
    "grossAmount" DOUBLE PRECISION NOT NULL,
    "taxWithheld" DOUBLE PRECISION NOT NULL,
    "netAmount" DOUBLE PRECISION NOT NULL,
    "userId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Dividend_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- AddForeignKey
ALTER TABLE "Transaction" ADD CONSTRAINT "Transaction_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Dividend" ADD CONSTRAINT "Dividend_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
