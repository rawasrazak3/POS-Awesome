<template>
  <div class="report-preview">
    <div class="text-center mb-2">
      <h1>VR Mania</h1>
      <div class="profile-name">{{ posProfile.name }}</div>
      <div class="subtitle">Daily Shift Report</div>
    </div>

    <div class="date-time mb-2">
      <span><strong>Date:</strong> {{ currentDate }}</span>
      <span class="time-right"><strong>Time:</strong> {{ currentTime }}</span>
    </div>

    <div class="section-title">Pay Transactions</div>
    <v-simple-table class="mb-2 pay-table">
      <tbody>
        <tr class="total-row">
          <td><strong>Total Pay In</strong></td>
          <td class="text-right"><strong>{{ formatCurrency(payInTotalDisplay) }}</strong></td>
        </tr>
        <tr v-for="(entry, index) in payData.payInEntries" :key="'payin-' + index">
          <td class="text-left">{{ entry.note }}</td>
          <td class="text-right">{{ formatCurrency(entry.amount) }}</td>
        </tr>
        <tr class="total-row">
          <td><strong>Total Pay Out</strong></td>
          <td class="text-right"><strong>{{ formatCurrency(payOutTotalDisplay) }}</strong></td>
        </tr>
        <tr v-for="(entry, index) in payData.payOutEntries" :key="'payout-' + index">
          <td class="text-left">{{ entry.note }}</td>
          <td class="text-right">{{ formatCurrency(entry.amount) }}</td>
        </tr>
        <tr class="remaining-row" data-test="remaining-row">
          <td><strong>Remaining</strong></td>
          <td class="text-right"><strong>{{ formatCurrency(remainingBalanceDisplay) }}</strong></td>
        </tr>
      </tbody>
    </v-simple-table>

    <div class="section-title">Items Sold</div>
    <v-simple-table class="mb-2">
      <thead>
        <tr>
          <th class="text-left">Item Name</th>
          <th class="text-center">Qty</th>
          <th class="text-right">Amount</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(item, index) in itemsSold" :key="index">
          <td>{{ item.item_name || item.name }}</td>
          <td class="text-center">{{ item.qty || item.quantity }}</td>
          <td class="text-right">{{ formatCurrency(item.amount) }}</td>
        </tr>
        <tr>
          <td colspan="2"><strong>Total Items Sold</strong></td>
          <td class="text-right"><strong>{{ formatCurrency(totalItemsSold) }}</strong></td>
        </tr>
      </tbody>
    </v-simple-table>

    <div class="section-title">Closing Shift Settlement</div>
    <v-simple-table class="mb-2 settlement-table">
      <thead>
        <tr>
          <th class="text-left">Payment Type</th>
          <th class="text-right">Closing</th>
          <th class="text-right">Expected</th>
          <th class="text-right">Diff</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(values, method) in paymentMethods" :key="method">
          <td class="text-left">{{ method }}</td>
          <td class="text-right">{{ formatCurrency(values.closing || 0) }}</td>
          <td class="text-right">{{ formatCurrency(values.expected || 0) }}</td>
          <td class="text-right">
            {{ formatCurrency((values.closing != null ? values.closing : 0) - (values.expected || 0)) }}
          </td>
        </tr>
        <tr class="total-row">
          <td><strong>Total</strong></td>
          <td class="text-right"><strong>{{ formatCurrency(totalClosing) }}</strong></td>
          <td class="text-right"><strong>{{ formatCurrency(totalExpected) }}</strong></td>
          <td class="text-right"><strong>{{ formatCurrency(totalDifference) }}</strong></td>
        </tr>
      </tbody>
    </v-simple-table>

    <div class="signature-section mt-4">
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
    computedPayInTotal() {
      return this.payData.payInEntries.reduce((sum, entry) => sum + (parseFloat(entry.amount) || 0), 0);
    },
    computedPayOutTotal() {
      return this.payData.payOutEntries.reduce((sum, entry) => sum + (parseFloat(entry.amount) || 0), 0);
    },
    computedRemainingBalance() {
      return this.computedPayInTotal - this.computedPayOutTotal;
    },
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
    currencySymbol() {
      return ""; // Remove currency symbol
    },
    formatCurrency(amount) {
      try {
        return Number(amount ?? 0).toFixed(2); // Plain number with two decimal places
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
                @page {
                  size: 80mm auto;
                  margin: 2mm;
                }
                body {
                  font-family: Arial, sans-serif;
                  margin: 0;
                  padding: 2mm;
                  width: 80mm;
                  font-size: 10px;
                  line-height: 1.2;
                }
                h1 {
                  font-size: 16px;
                  font-weight: bold;
                  margin: 0 0 2px;
                  text-align: center;
                }
                .profile-name {
                  font-size: 10px;
                  margin-bottom: 2px;
                }
                .subtitle {
                  font-size: 10px;
                  color: #555;
                  margin-bottom: 4px;
                  text-align: center;
                }
                .date-time {
                  display: flex;
                  justify-content: space-between;
                  font-size: 10px;
                  margin-bottom: 4px;
                }
                .time-right {
                  text-align: right;
                }
                .section-title {
                  font-size: 12px;
                  font-weight: bold;
                  margin: 4px 0 2px;
                  padding-bottom: 2px;
                  border-bottom: 1px solid #000;
                }
                table {
                  width: 100%;
                  border-collapse: collapse;
                  margin-bottom: 4px;
                }
                th, td {
                  padding: 2px;
                  border: 1px solid #000;
                  font-size: 10px;
                  word-wrap: break-word;
                }
                th {
                  font-weight: bold;
                  background-color: #f5f5f5;
                }
                .text-center {
                  text-align: center;
                }
                .text-right {
                  text-align: right;
                }
                .text-left {
                  text-align: left;
                }
                .total-row {
                  font-weight: bold;
                  background-color: #f9f9f9;
                  border: 1px solid #000;
                }
                .remaining-row {
                  font-weight: bold;
                }
                .pay-table td:first-child {
                  width: 70%;
                }
                .pay-table td:last-child {
                  width: 30%;
                }
                .settlement-table th:first-child,
                .settlement-table td:first-child {
                  width: 50%;
                }
                .settlement-table th:not(:first-child),
                .settlement-table td:not(:first-child) {
                  width: 16.67%;
                }
                .signature-section {
                  margin-top: 8px;
                }
                .signature-container {
                  display: flex;
                  justify-content: center;
                  align-items: center;
                }
                .signature-left {
                  text-align: center;
                  width: 100%;
                }
                .signature-line {
                  border-top: 1px solid #000;
                  width: 100%;
                  margin: 0 auto 4px;
                }
                @media print {
                  body {
                    margin: 0;
                    padding: 2mm;
                    width: 80mm;
                  }
                  .v-sheet, .v-table {
                    box-shadow: none !important;
                    border: none !important;
                  }
                  .v-table__wrapper > table {
                    border-spacing: 0;
                  }
                }
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
  padding: 2mm;
  width: 80mm;
  margin: 0 auto;
  font-family: Arial, sans-serif;
  font-size: 10px;
  line-height: 1.2;
}

h1 {
  font-size: 16px;
  font-weight: bold;
  margin: 0 0 2px;
  text-align: center;
}

.profile-name {
  font-size: 10px;
  margin-bottom: 2px;
}

.subtitle {
  font-size: 10px;
  color: #555;
  margin-bottom: 4px;
}

.date-time {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  margin-bottom: 4px;
}

.time-right {
  text-align: right;
}

.section-title {
  font-size: 12px;
  font-weight: bold;
  margin: 4px 0 2px;
  padding-bottom: 2px;
  border-bottom: 1px solid #000;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 4px;
}

th, td {
  padding: 2px;
  border: 1px solid #000;
  font-size: 10px;
  word-wrap: break-word;
}

th {
  font-weight: bold;
  background-color: #f5f5f5;
}

.pay-table td:first-child {
  width: 70%;
}

.pay-table td:last-child {
  width: 30%;
}

.settlement-table th:first-child,
.settlement-table td:first-child {
  width: 50%;
}

.settlement-table th:not(:first-child),
.settlement-table td:not(:first-child) {
  width: 16.67%;
}

.total-row {
  font-weight: bold;
  background-color: #f9f9f9;
  border: 1px solid #000;
}

.remaining-row {
  font-weight: bold;
}

.signature-section {
  margin-top: 8px;
}

.signature-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.signature-left {
  text-align: center;
  width: 100%;
}

.signature-line {
  border-top: 1px solid #000;
  width: 100%;
  margin: 0 auto 4px;
}
</style>