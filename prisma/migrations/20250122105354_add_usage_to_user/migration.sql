-- CreateTable
CREATE TABLE `User` (
    `id` VARCHAR(191) NOT NULL,
    `email` VARCHAR(191) NOT NULL,
    `password` VARCHAR(191) NOT NULL,
    `name` VARCHAR(191) NULL,
    `usage` INTEGER NOT NULL DEFAULT 0,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    UNIQUE INDEX `User_email_key`(`email`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Transaction` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `date` DATETIME(3) NOT NULL,
    `transactionType` VARCHAR(191) NOT NULL,
    `symbol` VARCHAR(191) NOT NULL,
    `operationType` VARCHAR(191) NOT NULL,
    `status` VARCHAR(191) NOT NULL,
    `currency` VARCHAR(191) NOT NULL,
    `orderQuantity` DOUBLE NOT NULL,
    `orderAmount` DOUBLE NOT NULL,
    `executedQuantity` DOUBLE NOT NULL,
    `averagePrice` DOUBLE NOT NULL,
    `transactionFee` DOUBLE NOT NULL,
    `transactionAmount` DOUBLE NOT NULL,
    `userId` VARCHAR(191) NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Dolar` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `gecerliOlduguTarih` VARCHAR(191) NOT NULL,
    `dovizAlis` DOUBLE NOT NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `YiUfe` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `yil` INTEGER NOT NULL,
    `ocak` DOUBLE NOT NULL,
    `subat` DOUBLE NOT NULL,
    `mart` DOUBLE NOT NULL,
    `nisan` DOUBLE NOT NULL,
    `mayis` DOUBLE NOT NULL,
    `haziran` DOUBLE NOT NULL,
    `temmuz` DOUBLE NOT NULL,
    `agustos` DOUBLE NOT NULL,
    `eylul` DOUBLE NOT NULL,
    `ekim` DOUBLE NOT NULL,
    `kasim` DOUBLE NOT NULL,
    `aralik` DOUBLE NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Dividend` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `paymentDate` DATETIME(3) NOT NULL,
    `symbol` VARCHAR(191) NOT NULL,
    `grossAmount` DOUBLE NOT NULL,
    `taxWithheld` DOUBLE NOT NULL,
    `netAmount` DOUBLE NOT NULL,
    `userId` VARCHAR(191) NOT NULL,
    `createdAt` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updatedAt` DATETIME(3) NOT NULL,

    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `Transaction` ADD CONSTRAINT `Transaction_userId_fkey` FOREIGN KEY (`userId`) REFERENCES `User`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `Dividend` ADD CONSTRAINT `Dividend_userId_fkey` FOREIGN KEY (`userId`) REFERENCES `User`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE;
