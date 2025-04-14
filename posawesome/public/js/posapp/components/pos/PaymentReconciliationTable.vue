<template>
  <v-data-table
    :headers="filteredHeaders"
    :items="paymentItems"
    class="closing-table"
    dense
    hide-default-footer
    :items-per-page="-1"
  >
    <template v-slot:item.closing="{ item }">
      <v-text-field
        v-model.number="item.closing"
        single-line
        type="number"
        step="0.01"
        outlined
        dense
        hide-details
        class="amount-field"
        @change="$emit('update-payment', item.mode_of_payment, item.closing)"
      />
    </template>
    <template v-if="!hideExpectedAmount" v-slot:item.expected="{ item }">
      <span class="text-center">{{ currencySymbol(currency) }} {{ formtCurrency(item.expected || 0) }}</span>
    </template>
    <template v-if="!hideExpectedAmount" v-slot:item.difference="{ item }">
      <span class="text-center" v-if="item.closing != null && item.closing !== 0">
        {{ currencySymbol(currency) }} {{ formtCurrency((item.closing || 0) - (item.expected || 0)) }}
      </span>
      <span class="text-center" v-else>{{ currencySymbol(currency) }} {{ formtCurrency(0) }}</span>
    </template>
  </v-data-table>
</template>

<script>
import format from "../../format";

export default {
  name: "PaymentReconciliationTable",
  mixins: [format],
  props: {
    paymentMethods: { type: Object, required: true },
    currency: { type: String, required: true },
    hideExpectedAmount: { type: Boolean, default: false },
  },
  computed: {
    filteredHeaders() {
      const baseHeaders = [
        { text: this.__("Payment Type"), value: "mode_of_payment", align: "left", class: "header-cell" },
        { text: this.__("Closing Amount"), value: "closing", align: "center", class: "header-cell" },
      ];
      if (!this.hideExpectedAmount) {
        baseHeaders.push(
          { text: this.__("Expected Amount"), value: "expected", align: "center", class: "header-cell" },
          { text: this.__("Excess/Short"), value: "difference", align: "center", class: "header-cell" }
        );
      }
      return baseHeaders;
    },
    paymentItems() {
      return Object.entries(this.paymentMethods).map(([mode, values]) => ({
        mode_of_payment: mode,
        expected: values.expected,
        closing: values.closing,
        difference: this.hideExpectedAmount
          ? null
          : values.closing != null && values.closing !== 0
            ? (values.closing || 0) - (values.expected || 0)
            : 0,
      }));
    },
  },
};
</script>

<style scoped>
.closing-table {
  border: 1px solid #d3d3d3;
  width: 100%;
}

.closing-table th {
  height: 64px;
  padding: 8px 24px;
  font-size: 48px;
  font-weight: 600;
  background-color: #f5f5f5;
  border-bottom: 2px solid #000;
}

.closing-table td {
  padding: 8px 24px;
}

.header-cell {
  text-align: inherit;
}

.amount-field {
  display: inline-flex;
  justify-content: center;
  width: 108px;
  padding: 6px;
}

.amount-field .v-input__slot {
  justify-content: center;
}

.amount-field .v-text-field__suffix {
  margin-left: 4px;
  color: #666;
  font-size: 12px;
}

.text-center {
  text-align: center;
}
</style>