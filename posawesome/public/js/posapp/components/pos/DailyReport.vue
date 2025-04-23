<template>
  <div class="report-preview">
    <div class="text-center mb-6">
      <h1>VR Mania</h1>
      <div>{{ posProfile.name }}</div>
      <div class="subtitle">Daily Shift Report</div>
    </div>

    <v-row class="mb-4">
      <v-col cols="6"><strong>Date:</strong> {{ currentDate }}</v-col>
      <v-col cols="6" class="text-right"><strong>Time:</strong> {{ currentTime }}</v-col>
    </v-row>

    <div class="section-title">Pay Transactions</div>
    <v-simple-table class="mb-4 pay-table">
      <tbody>
        <tr class="total-row">
          <td><strong>Total Pay In</strong></td>
          <td class="text-right"><strong>{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(payInTotalDisplay) }}</strong></td>
        </tr>
        <tr v-for="(entry, index) in payData.payInEntries" :key="'payin-' + index">
          <td class="text-left">{{ entry.note }}</td>
          <td class="text-right">{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(entry.amount) }}</td>
        </tr>
        <tr class="total-row">
          <td><strong>Total Pay Out</strong></td>
          <td class="text-right"><strong>{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(payOutTotalDisplay) }}</strong></td>
        </tr>
        <tr v-for="(entry, index) in payData.payOutEntries" :key="'payout-' + index">
          <td class="text-left">{{ entry.note }}</td>
          <td class="text-right">{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(entry.amount) }}</td>
        </tr>
        <tr class="remaining-row" data-test="remaining-row">
          <td><strong>Remaining</strong></td>
          <td class="text-right"><strong>{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(remainingBalanceDisplay) }}</strong></td>
        </tr>
      </tbody>
    </v-simple-table>

    <div class="section-title">Items Sold</div>
    <v-simple-table class="mb-4">
      <thead>
        <tr><th class="text-left">Item Name</th><th class="text-center">Qty</th><th class="text-right">Amount</th></tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in itemsSold" :key="index">
          <td>{{ item.item_name || item.name }}</td>
          <td class="text-center">{{ item.qty || item.quantity }}</td>
          <td class="text-right">{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(item.amount) }}</td>
        </tr>
        <tr>
          <td colspan="2"><strong>Total Items Sold</strong></td>
          <td class="text-right"><strong>{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(totalItemsSold) }}</strong></td>
        </tr>
      </tbody>
    </v-simple-table>

    <div class="section-title">Closing Shift Settlement</div>
    <v-simple-table class="mb-4 settlement-table">
      <thead>
        <tr>
          <th class="text-left" style="width: 40%;">Payment Type</th>
          <th class="text-right amount-column">Closing Amount</th>
          <th class="text-right amount-column">Expected Amount</th>
          <th class="text-right amount-column">Excess/Short</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(values, method) in paymentMethods" :key="method">
          <td class="text-left" style="width: 50%;">{{ method }}</td>
          <td class="text-right amount-column">{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(values.closing || 0) }}</td>
          <td class="text-right amount-column">{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(values.expected || 0) }}</td>
          <td class="text-right amount-column">
            {{ currencySymbol(posProfile.currency) }} {{ formatCurrency((values.closing != null ? values.closing : 0) - (values.expected || 0)) }}
          </td>
        </tr>
        <tr class="total-row">
          <td class="text-left" style="width: 50%;"><strong>Total</strong></td>
          <td class="text-right amount-column"><strong>{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(totalClosing) }}</strong></td>
          <td class="text-right amount-column"><strong>{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(totalExpected) }}</strong></td>
          <td class="text-right amount-column">
            <strong>{{ currencySymbol(posProfile.currency) }} {{ formatCurrency(totalDifference) }}</strong>
          </td>
        </tr>
      </tbody>
    </v-simple-table>

    <div class="signature-section mt-8">
      <div class="signature-container">
        <div class="signature-left">
          <div class="signature-line" />
          <div>Cashier's Signature</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import format from "../../format";

export default {
  name: "DailyReport",
  mixins: [format],
  props: {
    posProfile: {
      type: Object,
      required: true,
      validator: (prop) => typeof prop.name === "string" && typeof prop.currency === "string",
    },
    payData: {
      type: Object,
      required: true,
      default: () => ({
        payInEntries: [],
        payOutEntries: [],
        payInTotal: 0,
        payOutTotal: 0,
        remainingBalance: 0,
      }),
      validator: (payData) => {
        return (
          Array.isArray(payData.payInEntries) &&
          Array.isArray(payData.payOutEntries) &&
          typeof payData.payInTotal === "number" &&
          typeof payData.payOutTotal === "number" &&
          typeof payData.remainingBalance === "number"
        );
      },
    },
    itemsSold: {
      type: Array,
      required: true,
      default: () => [],
    },
    paymentMethods: {
      type: Object,
      required: true,
      default: () => ({}),
    },
    currentDate: {
      type: String,
      required: true,
    },
    currentTime: {
      type: String,
      required: true,
    },
  },
  computed: {
    // Compute totals from entries for reliability
    computedPayInTotal() {
      return this.payData.payInEntries.reduce((sum, entry) => sum + (parseFloat(entry.amount) || 0), 0);
    },
    computedPayOutTotal() {
      return this.payData.payOutEntries.reduce((sum, entry) => sum + (parseFloat(entry.amount) || 0), 0);
    },
    computedRemainingBalance() {
      return this.computedPayInTotal - this.computedPayOutTotal;
    },
    // Display values with prop fallback and discrepancy logging
    payInTotalDisplay() {
      const propTotal = parseFloat(this.payData.payInTotal) || 0;
      const computedTotal = this.computedPayInTotal;
      if (Math.abs(propTotal - computedTotal) > 0.01) {
        console.warn("payInTotal discrepancy:", { prop: propTotal, computed: computedTotal });
      }
      return computedTotal;
    },
    payOutTotalDisplay() {
      const propTotal = parseFloat(this.payData.payOutTotal) || 0;
      const computedTotal = this.computedPayOutTotal;
      if (Math.abs(propTotal - computedTotal) > 0.01) {
        console.warn("payOutTotal discrepancy:", { prop: propTotal, computed: computedTotal });
      }
      return computedTotal;
    },
    remainingBalanceDisplay() {
      const propBalance = parseFloat(this.payData.remainingBalance) || 0;
      const computedBalance = this.computedRemainingBalance;
      if (Math.abs(propBalance - computedBalance) > 0.01) {
        console.warn("remainingBalance discrepancy:", { prop: propBalance, computed: computedBalance });
      }
      return computedBalance;
    },
    totalItemsSold() {
      return this.itemsSold.reduce((sum, item) => sum + (parseFloat(item.amount) || 0), 0);
    },
    totalClosing() {
      return Object.values(this.paymentMethods).reduce((sum, method) => sum + (parseFloat(method.closing) || 0), 0);
    },
    totalExpected() {
      return Object.values(this.paymentMethods).reduce((sum, method) => sum + (parseFloat(method.expected) || 0), 0);
    },
    totalDifference() {
      return Object.values(this.paymentMethods).reduce((sum, method) => {
        return sum + ((method.closing != null ? parseFloat(method.closing) : 0) - (parseFloat(method.expected) || 0));
      }, 0);
    },
  },
  methods: {
    currencySymbol(currency) {
      try {
        const formatter = new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: currency || "USD",
        });
        return formatter.format(0).replace(/\d+([,.]\d+)?/, "").trim();
      } catch (error) {
        console.error("currencySymbol error:", error, { currency });
        return currency || "USD";
      }
    },
    formatCurrency(amount) {
      try {
        const currency = this.posProfile.currency || "USD";
        const formatted = new Intl.NumberFormat("en-US", {
          style: "currency",
          currency: currency,
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }).format(amount ?? 0);
        return formatted.replace(/^\D+/, "");
      } catch (error) {
        console.error("formatCurrency error:", error, { amount });
        return Number(amount ?? 0).toFixed(2);
      }
    },
    async getPrintContent() {
      try {
        console.log("getPrintContent payData:", JSON.stringify(this.payData, null, 2));
        const content = `
          <html>
            <head>
              <title>Daily Report - ${this.posProfile.name}</title>
              <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1 { font-size: 24px; font-weight: bold; margin-bottom: 4px; text-align: center; }
                .subtitle { font-size: 16px; color: #555; margin-bottom: 16px; text-align: center; }
                .section-title { font-size: 18px; font-weight: bold; margin: 16px 0 8px; padding-bottom: 4px; border-bottom: 1px solid #ddd; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 16px; }
                th, td { padding: 8px; border: 1px solid #ddd; }
                th { font-weight: bold; background-color: #f5f5f5; }
                .text-center { text-align: center; }
                .text-right { text-align: right; }
                .text-left { text-align: left; }
                .total-row { font-weight: bold; font-size: 16px; background-color: #f9f9f9; border: 2px solid #666; }
                .remaining-row { font-weight: bold; font-size: 16px; }
                .amount-column { width: 20%; min-width: 120px; }
                .settlement-table th:first-child, .settlement-table td:first-child { width: 40%; }
                .signature-section { margin-top: 32px; }
                .signature-container { display: flex; justify-content: space-between; align-items: center; }
                .signature-left, .signature-right { text-align: center; width: 40%; }
                .signature-line { border-top: 1px solid #000; width: 200px; margin: 0 auto 10px; }
              </style>
            </head>
            <body onload="window.print();">
              ${this.$el.innerHTML}
            </body>
          </html>
        `;
        console.log("getPrintContent length:", content.length);
        return content;
      } catch (error) {
        console.error("getPrintContent error:", {
          message: error.message,
          stack: error.stack,
        });
        throw new Error(__("Failed to generate print content: ") + (error.message || __("Unknown error")));
      }
    },
    // Methods to add/remove entries (optional, if managed in DailyReport)
    addPayIn(note, amount) {
      const newPayData = {
        ...this.payData,
        payInEntries: [...this.payData.payInEntries, { note, amount: parseFloat(amount) || 0 }],
      };
      this.$emit("update:payData", newPayData);
    },
    removePayIn(index) {
      const newPayData = {
        ...this.payData,
        payInEntries: this.payData.payInEntries.filter((_, i) => i !== index),
      };
      this.$emit("update:payData", newPayData);
    },
    addPayOut(note, amount) {
      const newPayData = {
        ...this.payData,
        payOutEntries: [...this.payData.payOutEntries, { note, amount: parseFloat(amount) || 0 }],
      };
      this.$emit("update:payData", newPayData);
    },
    removePayOut(index) {
      const newPayData = {
        ...this.payData,
        payOutEntries: this.payData.payOutEntries.filter((_, i) => i !== index),
      };
      this.$emit("update:payData", newPayData);
    },
    updateTotals() {
      const newPayData = {
        ...this.payData,
        payInTotal: this.computedPayInTotal,
        payOutTotal: this.computedPayOutTotal,
        remainingBalance: this.computedRemainingBalance,
      };
      this.$emit("update:payData", newPayData);
    },
  },
  created() {
    console.log("DailyReport created, payData:", JSON.stringify(this.payData, null, 2));
    this.$nextTick(() => {
      const remainingRow = document.querySelector('[data-test="remaining-row"]');
      console.log("Remaining row in DOM:", remainingRow, "Inner HTML:", remainingRow?.innerHTML);
      // Update totals on initialization
      this.updateTotals();
    });
  },
  watch: {
    "payData.payInEntries": {
      handler() {
        console.log("payInEntries changed, updating totals");
        this.updateTotals();
      },
      deep: true,
    },
    "payData.payOutEntries": {
      handler() {
        console.log("payOutEntries changed, updating totals");
        this.updateTotals();
      },
      deep: true,
    },
  },
};
</script>

<style scoped>
.report-preview {
  background: white;
  color: black;
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin: 16px 0 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid #ddd;
}

.signature-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.signature-left,
.signature-right {
  text-align: center;
  width: 40%;
}

.signature-line {
  border-top: 1px solid #000;
  width: 200px;
  margin: 0 auto 10px;
  height: 1px;
}

.pay-table .total-row td {
  font-size: 16px;
  border: 2px solid #666;
}

.pay-table .remaining-row td {
  font-size: 16px;
  font-weight: bold;
}

.settlement-table th:first-child,
.settlement-table td:first-child {
  width: 40%;
}
</style>