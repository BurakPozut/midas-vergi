import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { db } from "@/lib/prisma";
import { getDolarRate } from "@/lib/exchange";
import { getInflationRate } from "@/lib/inflation";

/**
 * Represents a transaction from the database
 * Contains all fields related to a buy or sell transaction
 */
interface Transaction {
  id: number;
  symbol: string;
  transactionType: string;
  operationType: string; // "Alış" (Buy) or "Satış" (Sell)
  status: string;
  orderQuantity: number;
  orderAmount: number;
  executedQuantity: number;
  averagePrice: number;
  currency: string;
  transactionFee: number;
  date: Date;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Represents an item in the FIFO queue for a symbol
 * Used to track buy transactions and their remaining quantities
 */
interface FifoQueueItem {
  quantity: number; // Remaining quantity of this buy lot
  price: number; // Price in TRY (converted from USD if necessary)
  date: Date; // Date of purchase (used for inflation adjustment)
}

/**
 * Summary of dividend income for the tax year
 * Includes totals and breakdown by symbol
 */
interface DividendSummary {
  total_gross_amount: number;
  total_tax_withheld: number;
  total_net_amount: number;
  dividends_by_symbol: { [key: string]: number };
}

/**
 * Final tax calculation results including:
 * - Profit/loss by symbol
 * - Total profits and losses
 * - Commission adjustments
 * - Dividend income
 * - Total taxable income
 */
interface ProfitLossResult {
  profit_loss_by_symbol: { [key: string]: number };
  total_profit: number;
  total_loss: number;
  total_profit_loss: number;
  total_profit_loss_after_commissions: number;
  dividend_summary: DividendSummary;
  total_taxable_income: number;
  missingBuyTransactions?: string[]; // Symbols where we found sells without matching buys
}

// Minimum inflation rate required to apply inflation adjustment to buy prices
const INFLATION_THRESHOLD = 10;

export async function POST() {
  try {
    // Authentication check
    const session = await auth();
    const userId = session?.user?.id;
    if (!userId) {
      console.log("No user ID found in session");
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    console.log("Processing tax calculation for user:", userId);

    // Track symbols where we find sells without matching buys
    const missingBuyTransactions: string[] = [];

    // Calculate tax year dates
    // We calculate tax for the previous year (e.g., in 2025, we calculate 2024's taxes)
    const currentYear = new Date().getFullYear();
    const taxYear = currentYear - 1;
    const startOfTaxYear = new Date(taxYear, 0, 1);
    const endOfTaxYear = new Date(taxYear, 11, 31, 23, 59, 59, 999);

    // Fetch ALL transactions for the user (not just tax year)
    // We need historical transactions to maintain accurate FIFO queues
    const allTransactions = await db.transaction.findMany({
      where: {
        userId: {
          equals: userId,
        },
      },
      orderBy: { date: "asc" },
    });
    console.log(`Found ${allTransactions.length} total transactions`);

    // Add detailed logging for debugging
    console.log("Transaction details:");
    allTransactions.forEach((transaction, index) => {
      console.log(`Transaction ${index + 1}:`);
      console.log(`  Symbol: ${transaction.symbol}`);
      console.log(`  Type: ${transaction.operationType}`);
      console.log(`  Date: ${transaction.date}`);
      console.log(`  Quantity: ${transaction.executedQuantity}`);
      console.log(`  Price: ${transaction.averagePrice}`);
      console.log(`  Amount: ${transaction.orderAmount}`);
      console.log(`  Currency: ${transaction.currency}`);
    });

    // Group transactions by symbol for easier processing
    // Each symbol will have its own array of transactions
    const transactionsBySymbol: { [key: string]: Transaction[] } = {};
    for (const transaction of allTransactions) {
      if (!transactionsBySymbol[transaction.symbol]) {
        transactionsBySymbol[transaction.symbol] = [];
      }
      transactionsBySymbol[transaction.symbol].push(transaction);
    }

    // Log symbols and transaction counts
    console.log("Transactions by symbol:");
    Object.keys(transactionsBySymbol).forEach((symbol) => {
      console.log(
        `${symbol}: ${transactionsBySymbol[symbol].length} transactions`
      );
    });

    // Initialize tracking objects
    const fifoQueues: { [key: string]: FifoQueueItem[] } = {}; // FIFO queues for each symbol
    const profitLoss: { [key: string]: number } = {}; // Profit/loss for each symbol
    let netProfit = 0;
    let netLoss = 0;

    // Process each symbol's transactions chronologically
    for (const [symbol, transactions] of Object.entries(transactionsBySymbol)) {
      console.log(`\nProcessing transactions for ${symbol}...`);
      fifoQueues[symbol] = [];

      // Sort all transactions by date to maintain FIFO order
      transactions.sort((a, b) => a.date.getTime() - b.date.getTime());

      // Process each transaction in chronological order
      for (const transaction of transactions) {
        const {
          operationType,
          executedQuantity,
          date,
          averagePrice,
          currency,
        } = transaction;

        // Check if this transaction is in the tax year
        // Only calculate profits/losses for tax year transactions
        const isTaxYearTransaction =
          date >= startOfTaxYear && date <= endOfTaxYear;

        console.log(
          `Transaction date: ${date.toISOString()}, Tax year: ${taxYear}`
        );
        console.log(
          `Tax year range: ${startOfTaxYear.toISOString()} to ${endOfTaxYear.toISOString()}`
        );
        console.log(`Is tax year transaction: ${isTaxYearTransaction}`);

        // Convert price to TRY if in USD
        let price = averagePrice;
        if (currency === "USD") {
          const rate = await getDolarRate(date);
          if (rate) {
            price *= rate;
          }
        }

        if (operationType === "Alış") {
          // For buy transactions:
          // Add to FIFO queue regardless of year
          // This maintains accurate stock holdings over time
          fifoQueues[symbol].push({
            quantity: executedQuantity,
            price,
            date,
          });
          console.log(
            `Added buy: ${symbol} - ${executedQuantity} @ ${price.toFixed(
              2
            )} TRY (${date.toISOString()})`
          );
        } else if (operationType === "Satış") {
          // For sell transactions:
          // Check if we have any matching buys in the FIFO queue
          if (!fifoQueues[symbol] || !fifoQueues[symbol].length) {
            console.log(
              `No buy transactions found for ${symbol} sell on ${date.toISOString()}`
            );
            if (!missingBuyTransactions.includes(symbol)) {
              missingBuyTransactions.push(symbol);
            }
            continue;
          }

          console.log(
            `Processing sell: ${symbol} - ${executedQuantity} @ ${price.toFixed(
              2
            )} TRY (${date.toISOString()})`
          );
          console.log(
            `Available buy lots for ${symbol}: ${fifoQueues[symbol].length}`
          );
          fifoQueues[symbol].forEach((buy, index) => {
            console.log(
              `  Lot ${index + 1}: ${buy.quantity} @ ${buy.price.toFixed(
                2
              )} TRY (${buy.date.toISOString()})`
            );
          });

          // Process the sell against available buys in FIFO order
          let remainingSellQuantity = executedQuantity;
          let totalProfit = 0;

          while (remainingSellQuantity > 0 && fifoQueues[symbol].length) {
            const buy = fifoQueues[symbol][0];
            let buyPrice = buy.price;

            // Only calculate inflation adjustment for tax year transactions
            if (isTaxYearTransaction) {
              const inflationRate = await getInflationRate(
                buy.date.getFullYear(),
                buy.date.getMonth(),
                date.getFullYear(),
                date.getMonth() - 1
              );

              console.log(
                `Inflation rate for ${buy.date.toISOString()} to ${date.toISOString()}: ${
                  inflationRate || 0
                }%`
              );

              // Apply inflation adjustment if above threshold
              if (inflationRate && inflationRate > INFLATION_THRESHOLD) {
                const oldBuyPrice = buyPrice;
                buyPrice *= 1 + inflationRate / 100;
                console.log(
                  `Applied inflation adjustment: ${oldBuyPrice.toFixed(
                    2
                  )} -> ${buyPrice.toFixed(2)} TRY`
                );
              }
            }

            if (buy.quantity <= remainingSellQuantity) {
              // If the entire buy lot is used:
              // Calculate profit/loss (only for tax year transactions)
              if (isTaxYearTransaction) {
                const profit = (price - buyPrice) * buy.quantity;
                totalProfit += profit;
                console.log(
                  `Used entire buy lot: ${buy.quantity} @ ${buyPrice.toFixed(
                    2
                  )} TRY`
                );
                console.log(`Profit from this lot: ${profit.toFixed(2)} TRY`);
              }
              remainingSellQuantity -= buy.quantity;
              fifoQueues[symbol].shift(); // Remove the used buy lot
            } else {
              // If only part of the buy lot is used:
              // Calculate profit/loss for the used portion
              if (isTaxYearTransaction) {
                const profit = (price - buyPrice) * remainingSellQuantity;
                totalProfit += profit;
                console.log(
                  `Used partial buy lot: ${remainingSellQuantity} of ${
                    buy.quantity
                  } @ ${buyPrice.toFixed(2)} TRY`
                );
                console.log(`Profit from this lot: ${profit.toFixed(2)} TRY`);
              }
              buy.quantity -= remainingSellQuantity;
              remainingSellQuantity = 0;
            }
          }

          if (isTaxYearTransaction) {
            console.log(
              `Total profit for this sell: ${totalProfit.toFixed(2)} TRY`
            );

            // Update profit/loss tracking
            if (!profitLoss[symbol]) {
              profitLoss[symbol] = 0;
            }
            profitLoss[symbol] += totalProfit;

            if (totalProfit > 0) {
              netProfit += totalProfit;
            } else {
              netLoss += Math.abs(totalProfit);
            }

            console.log(
              `Updated profit/loss for ${symbol}: ${profitLoss[symbol].toFixed(
                2
              )} TRY`
            );
            console.log(`Net profit so far: ${netProfit.toFixed(2)} TRY`);
            console.log(`Net loss so far: ${netLoss.toFixed(2)} TRY`);
          }
        }
      }
    }

    // Calculate commissions for tax year transactions only
    console.log(`\nCalculating tax year ${taxYear} commissions...`);
    let totalCommission = 0;
    const taxYearTransactions = allTransactions.filter(
      (t) => t.date >= startOfTaxYear && t.date <= endOfTaxYear
    );

    for (const t of taxYearTransactions) {
      let commission = t.transactionFee;
      if (t.currency === "USD") {
        const rate = await getDolarRate(t.date);
        if (rate) {
          commission *= rate;
        }
      }
      totalCommission += commission;
    }

    // Process dividends for the tax year
    console.log(`\nProcessing tax year ${taxYear} dividends...`);
    const dividends = await db.dividend.findMany({
      where: {
        userId: {
          equals: userId,
        },
        paymentDate: {
          gte: startOfTaxYear,
          lte: endOfTaxYear,
        },
      },
      orderBy: { paymentDate: "asc" },
    });

    // Initialize dividend summary
    const dividendSummary: DividendSummary = {
      total_gross_amount: 0,
      total_tax_withheld: 0,
      total_net_amount: 0,
      dividends_by_symbol: {},
    };

    // Process each dividend payment
    for (const dividend of dividends) {
      let grossAmount = dividend.grossAmount;
      let taxWithheld = dividend.taxWithheld;
      let netAmount = dividend.netAmount;

      // Convert USD amounts to TRY if needed
      const rate = await getDolarRate(dividend.paymentDate);
      if (rate) {
        grossAmount *= rate;
        taxWithheld *= rate;
        netAmount *= rate;
      }

      // Update dividend totals
      dividendSummary.total_gross_amount += grossAmount;
      dividendSummary.total_tax_withheld += taxWithheld;
      dividendSummary.total_net_amount += netAmount;

      // Track dividends by symbol
      if (dividend.symbol in dividendSummary.dividends_by_symbol) {
        dividendSummary.dividends_by_symbol[dividend.symbol] += grossAmount;
      } else {
        dividendSummary.dividends_by_symbol[dividend.symbol] = grossAmount;
      }
    }

    // Calculate final totals
    const totalPL = Object.values(profitLoss).reduce(
      (sum, val) => sum + val,
      0
    );
    const finalPL = totalPL - totalCommission;

    // Total taxable income includes both capital gains and dividend income
    const totalTaxableIncome = finalPL + dividendSummary.total_gross_amount;

    console.log("\n=== FINAL CALCULATION SUMMARY ===");
    console.log(`Total Profit/Loss by Symbol:`);
    Object.entries(profitLoss).forEach(([symbol, amount]) => {
      console.log(`  ${symbol}: ${amount.toFixed(2)} TRY`);
    });
    console.log(`Total Net Profit: ${netProfit.toFixed(2)} TRY`);
    console.log(`Total Net Loss: ${netLoss.toFixed(2)} TRY`);
    console.log(`Total P/L (before commissions): ${totalPL.toFixed(2)} TRY`);
    console.log(`Total Commissions: ${totalCommission.toFixed(2)} TRY`);
    console.log(`Final P/L (after commissions): ${finalPL.toFixed(2)} TRY`);
    console.log(`Dividend Summary:`);
    console.log(
      `  Total Gross Amount: ${dividendSummary.total_gross_amount.toFixed(
        2
      )} TRY`
    );
    console.log(
      `  Total Tax Withheld: ${dividendSummary.total_tax_withheld.toFixed(
        2
      )} TRY`
    );
    console.log(
      `  Total Net Amount: ${dividendSummary.total_net_amount.toFixed(2)} TRY`
    );
    console.log(`  Dividends by Symbol:`);
    Object.entries(dividendSummary.dividends_by_symbol).forEach(
      ([symbol, amount]) => {
        console.log(`    ${symbol}: ${amount.toFixed(2)} TRY`);
      }
    );
    console.log(`Total Taxable Income: ${totalTaxableIncome.toFixed(2)} TRY`);
    if (missingBuyTransactions.length > 0) {
      console.log(
        `Missing Buy Transactions for: ${missingBuyTransactions.join(", ")}`
      );
    }

    // Prepare the final result object
    const result: ProfitLossResult = {
      profit_loss_by_symbol: profitLoss,
      total_profit: netProfit,
      total_loss: netLoss,
      total_profit_loss: totalPL,
      total_profit_loss_after_commissions: finalPL,
      dividend_summary: dividendSummary,
      total_taxable_income: totalTaxableIncome,
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
