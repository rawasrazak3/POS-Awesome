<!-- DailyReport.vue -->
<template>
    <div class="report-preview">
      <div class="text-center mb-6">
        <h1>VR Mania Avenues</h1>
        <div class="subtitle">Daily Shift Report</div>
      </div>
  
      <v-row class="mb-4">
        <v-col cols="6"><strong>Date:</strong> {{ currentDate }}</v-col>
        <v-col cols="6" class="text-right"><strong>Time:</strong> {{ currentTime }}</v-col>
      </v-row>
  
      <div class="section-title">Pay Transactions</div>
      <v-simple-table class="mb-4">
        <tbody>
          <tr><td><strong>Pay In</strong></td><td class="text-right">{{ currencySymbol(posProfile.currency) }} {{ formtCurrency(payData.payInTotal) }}</td></tr>
          <tr v-for="(entry, index) in payData.payInEntries" :key="'payin-' + index"><td><strong>Note</strong></td><td class="pl-6 text-right">{{ entry.note }}</td></tr>
          <tr><td><strong>Pay Out</strong></td><td class="text-right">{{ currencySymbol(posProfile.currency) }} {{ formtCurrency(payData.payOutTotal) }}</td></tr>
          <tr v-for="(entry, index) in payData.payOutEntries" :key="'payout-' + index"><td><strong>Note</strong></td><td class="pl-6 text-right">{{ entry.note }}</td></tr>
          <tr><td><strong>Remaining</strong></td><td class="text-right">{{ currencySymbol(posProfile.currency) }} {{ formtCurrency(payData.payInTotal - payData.payOutTotal) }}</td></tr>
        </tbody>
      </v-simple-table>
  
      <div class="section-title">Items Sold</div>
      <v-simple-table class="mb-4">
        <thead>
          <tr><th>Item Name</th><th class="text-center">Qty</th><th class="text-right">Amount</th></tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in itemsSold" :key="index">
            <td>{{ item.item_name || item.name }}</td>
            <td class="text-center">{{ item.qty || item.quantity }}</td>
            <td class="text-right">{{ currencySymbol(posProfile.currency) }} {{ formtCurrency(item.amount) }}</td>
          </tr>
          <tr>
            <td colspan="2"><strong>Total Items Sold</strong></td>
            <td class="text-right"><strong>{{ currencySymbol(posProfile.currency) }} {{ formtCurrency(totalItemsSold) }}</strong></td>
          </tr>
        </tbody>
      </v-simple-table>
  
      <div class="section-title">Closing Shift Settlement</div>
      <v-simple-table class="mb-4 settlement-table">
        <thead>
          <tr><th class="text-left">Payment Type</th><th class="text-right">Closing Amount</th><th class="text-right">Expected Amount</th><th class="text-right">Difference</th></tr>
        </thead>
        <tbody>
          <tr v-for="(values, method) in paymentMethods" :key="method">
            <td class="text-left">{{ method }}</td>
            <td class="text-right">{{ currencySymbol(posProfile.currency) }} {{ formtCurrency(values.closing || 0) }}</td>
            <td class="text-right">{{ currencySymbol(posProfile.currency) }} {{ formtCurrency(values.expected || 0) }}</td>
            <td class="text-right">{{ currencySymbol(posProfile.currency) }} {{ formtCurrency((values.expected || 0) - (values.closing || 0)) }}</td>
          </tr>
          <tr class="total-row">
            <td class="text-left"><strong>Total</strong></td>
            <td class="text-right"><strong>{{ currencySymbol(posProfile.currency) }} {{ formtCurrency(totalClosing) }}</strong></td>
            <td class="text-right"><strong>{{ currencySymbol(posProfile.currency) }} {{ formtCurrency(totalExpected) }}</strong></td>
            <td class="text-right"><strong>{{ currencySymbol(posProfile.currency) }} {{ formtCurrency(totalDifference) }}</strong></td>
          </tr>
        </tbody>
      </v-simple-table>
  
      <div class="signature-section mt-8">
        <v-row>
          <v-col cols="6" class="text-center"><div class="signature-line" /><div>Cashier's Signature</div></v-col>
          <v-col cols="6" class="text-center"><div class="signature-line" /><div>Manager's Signature</div></v-col>
        </v-row>
      </div>
    </div>
  </template>
  
  <script>
  import format from "../../format";
  
  export default {
    name: "DailyReport",
    mixins: [format],
    props: {
      posProfile: { type: Object, required: true },
      payData: { type: Object, required: true },
      itemsSold: { type: Array, required: true },
      paymentMethods: { type: Object, required: true },
      currentDate: { type: String, required: true },
      currentTime: { type: String, required: true },
    },
    computed: {
      totalItemsSold() {
        return this.itemsSold.reduce((sum, item) => sum + (item.amount || 0), 0);
      },
      totalClosing() {
        return Object.values(this.paymentMethods).reduce((sum, method) => sum + (parseFloat(method.closing) || 0), 0);
      },
      totalExpected() {
        return Object.values(this.paymentMethods).reduce((sum, method) => sum + (parseFloat(method.expected) || 0), 0);
      },
      totalDifference() {
        return this.totalExpected - this.totalClosing;
      },
    },
    methods: {
      async getPrintContent() {
        return `
          <html>
            <head>
              <title>Daily Report - VR Mania</title>
              <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1 { font-size: 24px; font-weight: bold; margin-bottom: 4px; text-align: center; }
                .subtitle { font-size: 16px; color: #555; margin-bottom: 16px; text-align: center; }
                .section-title { font-size: 18px; font-weight: bold; margin: 16px 0 8px; padding-bottom: 4px; border-sizing: 1px solid #ddd; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 16px; }
                th, td { padding: 8px; border: 1px solid #ddd; }
                th { font-weight: bold; background-color: #f5f5f5; }
                .text-center { text-align: center; }
                .text-right { text-align: right; }
                .text-left { text-align: left; }
                .total-row { font-weight: bold; background-color: #f9f9f9; }
                .signature-section { margin-top: 32px; }
                .signature-line { border-top: 1px solid #000; width: 200px; margin: 0 auto 10px; }
                .pl-6 { padding-left: 24px; }
              </style>
            </head>
            <body onload="window.print();">
              ${this.$el.innerHTML}
            </body>
          </html>
        `;
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
  
  .signature-line {
    border-top: 1px solid #000;
    width: 200px;
    margin: 0 auto 10px;
    height: 1px;
  }
  </style>