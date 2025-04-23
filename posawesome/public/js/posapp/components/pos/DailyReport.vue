<template>
  <div class="report-preview">
    <div class="text-center mb-2">
      <h1>VR Mania</h1>
      <div class="profile-name">{{ posProfile.name }}</div>
      <div class="subtitle">Daily Shift Report</div>
      <div class="date-time">
        <span><strong>Date:</strong> {{ currentDate }}</span>
        <span class="time-right"><strong>Time:</strong> {{ currentTime }}</span>
      </div>
      <div class="user-name-container text-left"><strong>POS User: </strong>{{ userName }}</div>
    </div>

    <div class="section-title">Pay Transactions</div>
    <v-simple-table class="mb-2 pay-table">
      <tbody>
        <tr v-for="(row, index) in payRows" :key="index" :class="row.class" :data-test="row.test">
          <td :class="{ 'text-left': row.note }">{{ row.label }}</td>
          <td class="text-right">{{ formatCurrency(row.amount) }}</td>
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
          <td class="text-right"><strong>{{ formatCurrency(totals.itemsSoldTotal) }}</strong></td>
        </tr>
      </tbody>
    </v-simple-table>

    <div class="section-title">Closing Shift Settlement</div>
    <v-simple-table class="mb-2 settlement-table">
      <thead>
        <tr>
          <th class="text-left">Payment Type</th>
          <th class="text-right">Closing</th>
          <th class="text-right">Diff</th>
          <th class="text-right">Expected</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(values, method) in paymentMethods" :key="method">
          <td class="text-left">{{ method }}</td>
          <td class="text-right">{{ formatCurrency(values.closing || 0) }}</td>
          <td class="text-right">{{ formatCurrency((values.closing || 0) - (values.expected || 0)) }}</td>
          <td class="text-right">{{ formatCurrency(values.expected || 0) }}</td>
        </tr>
        <tr class="total-row">
          <td>Total</td>
          <td class="text-right">{{ formatCurrency(totals.closingTotal) }}</td>
          <td class="text-right">{{ formatCurrency(totals.differenceTotal) }}</td>
          <td class="text-right">{{ formatCurrency(totals.expectedTotal) }}</td>
        </tr>
      </tbody>
    </v-simple-table>

    <div class="signature-section">
      <div class="signature-line"></div>
      <div class="text-center">Cashier's Name & Signature</div>
    </div>
  </div>
</template>

<script>
import format from '../../format';

export default {
  name: 'DailyReport',
  mixins: [format],
  props: {
    posProfile: {
      type: Object,
      required: true,
      validator: (prop) => typeof prop.name === 'string' && typeof prop.currency === 'string',
    },
    userName: {
      type: String,
      required: true,
      default: 'Unknown User',
    },
    payData: {
      type: Object,
      required: true,
      default: () => ({ payInEntries: [], payOutEntries: [], payInTotal: 0, payOutTotal: 0, remainingBalance: 0 }),
      validator: (payData) => (
        Array.isArray(payData.payInEntries) &&
        Array.isArray(payData.payOutEntries) &&
        typeof payData.payInTotal === 'number' &&
        typeof payData.payOutTotal === 'number' &&
        typeof payData.remainingBalance === 'number'
      ),
    },
    itemsSold: { type: Array, required: true, default: () => [] },
    paymentMethods: { type: Object, required: true, default: () => ({}) },
    currentDate: { type: String, required: true },
    currentTime: { type: String, required: true },
  },
  computed: {
    payRows() {
      return [
        { label: 'Total Pay In', amount: this.totals.payInTotal, class: 'total-row' },
        ...this.payData.payInEntries.map((entry, index) => ({
          label: entry.note,
          amount: entry.amount,
          class: '',
          key: `payin-${index}`,
          note: true,
        })),
        { label: 'Total Pay Out', amount: this.totals.payOutTotal, class: 'total-row' },
        ...this.payData.payOutEntries.map((entry, index) => ({
          label: entry.note,
          amount: entry.amount,
          class: '',
          key: `payout-${index}`,
          note: true,
        })),
        { label: 'Remaining', amount: this.totals.remainingBalance, class: 'remaining-row', test: 'remaining-row' },
      ];
    },
    totals() {
      const payInTotal = this.payData.payInEntries.reduce((sum, entry) => sum + (parseFloat(entry.amount) || 0), 0);
      const payOutTotal = this.payData.payOutEntries.reduce((sum, entry) => sum + (parseFloat(entry.amount) || 0), 0);
      const itemsSoldTotal = this.itemsSold.reduce((sum, item) => sum + (parseFloat(item.amount) || 0), 0);
      const closingTotal = Object.values(this.paymentMethods).reduce((sum, method) => sum + (parseFloat(method.closing) || 0), 0);
      const expectedTotal = Object.values(this.paymentMethods).reduce((sum, method) => sum + (parseFloat(method.expected) || 0), 0);
      const differenceTotal = Object.values(this.paymentMethods).reduce(
        (sum, method) => sum + ((method.closing || 0) - (method.expected || 0)),
        0
      );
      return {
        payInTotal,
        payOutTotal,
        remainingBalance: payInTotal - payOutTotal,
        itemsSoldTotal,
        closingTotal,
        expectedTotal,
        differenceTotal,
      };
    },
  },
  methods: {
    currencySymbol() {
      return '';
    },
    formatCurrency(amount) {
      try {
        return Number(amount ?? 0).toFixed(2);
      } catch (error) {
        console.error('formatCurrency error:', error, { amount });
        return Number(amount ?? 0).toFixed(2);
      }
    },
    updatePayData({ action, type, note, amount, index }) {
      const newPayData = { ...this.payData };
      if (action === 'add') {
        newPayData[`${type}Entries`] = [...newPayData[`${type}Entries`], { note, amount: parseFloat(amount) || 0 }];
      } else if (action === 'remove') {
        newPayData[`${type}Entries`] = newPayData[`${type}Entries`].filter((_, i) => i !== index);
      }
      newPayData.payInTotal = newPayData.payInEntries.reduce((sum, entry) => sum + (parseFloat(entry.amount) || 0), 0);
      newPayData.payOutTotal = newPayData.payOutEntries.reduce((sum, entry) => sum + (parseFloat(entry.amount) || 0), 0);
      newPayData.remainingBalance = newPayData.payInTotal - newPayData.payOutTotal;
      this.$emit('update:payData', newPayData);
    },
    async getPrintContent() {
      try {
        const content = `
          <html>
            <head>
              <title>Daily Report - ${this.posProfile.name}</title>
              <style>
                :root {
                  --page-width: 80mm;
                  --margin: 2mm;
                  --font-size: 10px;
                  --border-color: #000;
                  --border-table: 1.5px solid var(--border-color);
                  --border-signature: 2px solid var(--border-color);
                }
                @page { size: var(--page-width) auto; margin: var(--margin); }
                body { font-family: Arial, sans-serif; margin: 0; padding: var(--margin); width: var(--page-width); font-size: var(--font-size); line-height: 1.2; }
                h1 { font-size: 16px; font-weight: bold; margin: 0 0 2px; text-align: center; }
                .profile-name, .user-name-container, .subtitle { font-size: var(--font-size); }
                .profile-name { margin-bottom: 2px; text-align: center; }
                .user-name-container { margin-bottom: 4px; text-align: left; }
                .subtitle { color: #555; margin-bottom: 4px; text-align: center; }
                .date-time { display: flex; justify-content: space-between; font-size: var(--font-size); margin-bottom: 4px; }
                .section-title { font-size: 12px; font-weight: bold; margin: 4px 0 2px; padding-bottom: 2px; border-bottom: 1px solid var(--border-color); }
                table { width: 100%; border-collapse: collapse; margin-bottom: 4px; }
                th, td { padding: 2px; border: var(--border-table); border-top: none; font-size: var(--font-size); word-wrap: break-word; }
                th { font-weight: bold; background-color: #f5f5f5; }
                .text-center { text-align: center; }
                .text-right { text-align: right; }
                .text-left { text-align: left; }
                .total-row, .remaining-row { border: var(--border-table); border-top: none; }
                .total-row { background-color: #f9f9f9; }
                .pay-table td:first-child { width: 70%; }
                .pay-table td:last-child { width: 30%; }
                .settlement-table th:first-child, .settlement-table td:first-child { width: 50%; }
                .settlement-table th:not(:first-child), .settlement-table td:not(:first-child) { width: 16.67%; }
                .signature-section { margin-top: 48px; text-align: center; }
                .signature-line { border-top: var(--border-signature); margin: 0 auto 4px; width: 100%; }
                @media print {
                  body { margin: 0; padding: var(--margin); width: var(--page-width); }
                  .v-sheet, .v-table { box-shadow: none !important; border: none !important; }
                  .v-table__wrapper table th, .v-table__wrapper table td { border: var(--border-table); border-top: none !important; }
                  .v-table__wrapper > table { border-spacing: 0; }
                }
              </style>
            </head>
            <body>${this.$el.innerHTML}</body>
          </html>
        `;
        console.log("Generated print content with userName:", this.userName);
        return content;
      } catch (error) {
        console.error('getPrintContent error:', error);
        throw new Error('Failed to generate print content');
      }
    },
  },
  created() {
    this.$nextTick(() => {
      const remainingRow = document.querySelector('[data-test="remaining-row"]');
      console.log('Remaining row:', remainingRow?.innerHTML);
      console.log('User name:', this.userName, 'positioned below date');
    });
  },
  mounted() {
    console.log('DailyReport component mounted');
  },
};
</script>

<style scoped>
.report-preview {
  --page-width: 80mm;
  --margin: 2mm;
  --font-size: 10px;
  --border-color: #000;
  --border-table: 1.5px solid var(--border-color);
  --border-signature: 2px solid var(--border-color);
  background: white;
  color: black;
  padding: var(--margin);
  width: var(--page-width);
  margin: 0 auto;
  font-family: Arial, sans-serif;
  font-size: var(--font-size);
  line-height: 1.2;
}
h1 { font-size: 16px; font-weight: bold; margin: 0 0 2px; }
.profile-name, .user-name-container, .subtitle { font-size: var(--font-size); }
.profile-name { margin-bottom: 2px; text-align: center; }
.user-name-container { margin-bottom: 4px; text-align: left;font-weight: 600;}
.subtitle { color: #555; margin-bottom: 4px; text-align: center; }
.date-time { display: flex; justify-content: space-between; margin-bottom: 4px; }
.section-title { font-size: 12px; font-weight: bold; margin: 4px 0 2px; padding-bottom: 2px; border-bottom: 1px solid var(--border-color); }
table { width: 100%; border-collapse: collapse; margin-bottom: 4px; }
th, td { padding: 2px; border: var(--border-table); border-top: none; font-size: var(--font-size); word-wrap: break-word; }
th { font-weight: bold; background-color: #f5f5f5; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-left { text-align: left; }
.total-row, .remaining-row { border: var(--border-table); border-top: none; }
.total-row { background-color: #f9f9f9; }
.pay-table td:first-child { width: 70%; }
.pay-table td:last-child { width: 30%; }
.settlement-table th:first-child, .settlement-table td:first-child { width: 50%; }
.settlement-table th:not(:first-child), .settlement-table td:not(:first-child) { width: 16.67%; }
.signature-section { margin-top: 48px; text-align: center; }
.signature-line { border-top: var(--border-signature); margin: 0 auto 4px; width: 100%; }
</style>