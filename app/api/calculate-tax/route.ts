import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { db } from "@/lib/prisma";
import { getDolarRate } from "@/lib/exchange";
import { getInflationRate } from "@/lib/inflation";

interface FifoQueueItem {
  quantity: number;
  price: number;
  date: Date;
}

interface ProfitLossResult {
  profit_loss_by_symbol: { [key: string]: number };
  total_profit: number;
  total_loss: number;
  total_profit_loss: number;
  total_profit_loss_after_commissions: number;
  missingBuyTransactions?: string[];
}

const INFLATION_THRESHOLD = 10;

export async function POST() {
  try {
    const session = await auth();
    const userId = session?.user?.id;
    if (!userId) {
      console.log("No user ID found in session");
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    console.log("Processing tax calculation for user:", userId);

    // Add array to track missing buy transactions
    const missingBuyTransactions: string[] = [];

    // Get all transactions for the user
    const transactions = await db.transaction.findMany({
      where: {
        userId: {
          equals: userId,
        },
      },
      orderBy: { date: "asc" },
    });
    // console.log(
    //   "Raw transactions from DB:",
    //   JSON.stringify(transactions, null, 2)
    // );
    console.log(`Found ${transactions.length} total transactions`);

    if (!transactions.length) {
      console.log("No transactions found for user");
      return NextResponse.json(
        { error: "No transactions found" },
        { status: 404 }
      );
    }

    // Separate buy and sell transactions
    const buyTransactions = transactions.filter(
      (t) => t.operationType === "Alış"
    );
    const sellTransactions = transactions.filter(
      (t) => t.operationType === "Satış"
    );
    console.log(`Buy transactions: ${buyTransactions.length}`);
    console.log(`Sell transactions: ${sellTransactions.length}`);

    // Initialize tracking
    const fifoQueues: { [key: string]: FifoQueueItem[] } = {};
    const profitLoss: { [key: string]: number } = {};
    let netProfit = 0;
    let netLoss = 0;

    // Process buy transactions
    console.log("\nProcessing buy transactions...");
    for (const transaction of buyTransactions) {
      const { symbol, executedQuantity, date, averagePrice, currency } =
        transaction;
      console.log(
        `\nProcessing buy: ${symbol} - ${executedQuantity} @ ${averagePrice} ${currency}`
      );

      let price = averagePrice;
      if (currency === "USD") {
        const rate = await getDolarRate(date);
        console.log(`USD conversion rate: ${rate}`);
        if (rate) {
          price *= rate;
          console.log(`Converted price: ${price} TRY`);
        }
      }

      if (executedQuantity > 0) {
        if (!fifoQueues[symbol]) {
          fifoQueues[symbol] = [];
        }
        fifoQueues[symbol].push({
          quantity: executedQuantity,
          price,
          date,
        });
        console.log(
          `Added to queue: ${executedQuantity} units at ${price} TRY`
        );
      }
    }

    // Process sell transactions
    console.log("\nProcessing sell transactions...");
    for (const transaction of sellTransactions) {
      const { symbol, executedQuantity, date, averagePrice, currency } =
        transaction;
      console.log(
        `\nProcessing sell: ${symbol} - ${executedQuantity} @ ${averagePrice} ${currency}`
      );

      let sellPrice = averagePrice;
      if (currency === "USD") {
        const rate = await getDolarRate(date);
        console.log(`USD conversion rate: ${rate}`);
        if (rate) {
          sellPrice *= rate;
          console.log(`Converted sell price: ${sellPrice} TRY`);
        }
      }

      if (!fifoQueues[symbol] || !fifoQueues[symbol].length) {
        console.log(`No buy transactions found for ${symbol}, skipping`);
        if (!missingBuyTransactions.includes(symbol)) {
          missingBuyTransactions.push(symbol);
        }
        continue;
      }

      let remainingSellQuantity = executedQuantity;
      let totalProfit = 0;

      while (remainingSellQuantity > 0 && fifoQueues[symbol].length) {
        const buy = fifoQueues[symbol][0];
        let buyPrice = buy.price;
        console.log(
          `Matching with buy: ${buy.quantity} units at ${buyPrice} TRY`
        );

        // Calculate inflation adjustment
        const buyDate = buy.date;
        const inflationRate = await getInflationRate(
          buyDate.getFullYear(),
          buyDate.getMonth(),
          date.getFullYear(),
          date.getMonth() - 1
        );
        console.log(`Inflation rate: ${inflationRate}%`);

        if (inflationRate && inflationRate > INFLATION_THRESHOLD) {
          const oldPrice = buyPrice;
          buyPrice *= 1 + inflationRate / 100;
          console.log(
            `Applied inflation adjustment: ${oldPrice} -> ${buyPrice} TRY`
          );
        }

        if (buy.quantity <= remainingSellQuantity) {
          const profit = (sellPrice - buyPrice) * buy.quantity;
          totalProfit += profit;
          remainingSellQuantity -= buy.quantity;
          fifoQueues[symbol].shift();
          console.log(
            `Used entire lot. Profit: ${profit} TRY. Remaining to sell: ${remainingSellQuantity}`
          );
        } else {
          const profit = (sellPrice - buyPrice) * remainingSellQuantity;
          totalProfit += profit;
          buy.quantity -= remainingSellQuantity;
          remainingSellQuantity = 0;
          console.log(
            `Used partial lot. Profit: ${profit} TRY. Remaining in buy lot: ${buy.quantity}`
          );
        }
      }

      console.log(`Total profit for this sale: ${totalProfit} TRY`);
      profitLoss[symbol] = (profitLoss[symbol] || 0) + totalProfit;
      if (totalProfit > 0) {
        netProfit += totalProfit;
      } else {
        netLoss += totalProfit;
      }
    }

    // Calculate total commission
    console.log("\nCalculating commissions...");
    let totalCommission = 0;
    for (const t of transactions) {
      let commission = t.transactionFee;
      console.log(`Processing commission: ${commission} ${t.currency}`);
      if (t.currency === "USD") {
        const rate = await getDolarRate(t.date);
        console.log(`Commission USD rate: ${rate}`);
        if (rate) {
          commission *= rate;
          console.log(`Converted commission: ${commission} TRY`);
        }
      }
      totalCommission += commission;
    }
    console.log(`Total commission: ${totalCommission} TRY`);

    const totalPL = Object.values(profitLoss).reduce(
      (sum, val) => sum + val,
      0
    );
    const finalPL = totalPL - totalCommission;

    console.log("\nFinal Results:");
    console.log("Profit/Loss by symbol:", profitLoss);
    console.log(`Total Profit: ${netProfit} TRY`);
    console.log(`Total Loss: ${netLoss} TRY`);
    console.log(`Total P/L: ${totalPL} TRY`);
    console.log(`Final P/L after commissions: ${finalPL} TRY`);

    const result: ProfitLossResult = {
      profit_loss_by_symbol: profitLoss,
      total_profit: netProfit,
      total_loss: netLoss,
      total_profit_loss: totalPL,
      total_profit_loss_after_commissions: finalPL,
      missingBuyTransactions:
        missingBuyTransactions.length > 0 ? missingBuyTransactions : undefined,
    };

    return NextResponse.json(result);
  } catch (error) {
    console.error("Error calculating tax:", error);
    if (error instanceof Error) {
      console.error("Error details:", error.message);
      console.error("Stack trace:", error.stack);
    }
    return NextResponse.json(
      { error: "Error calculating tax" },
      { status: 500 }
    );
  }
}
