<!-- PaymentReconciliationTable.vue -->
<template>
    <v-simple-table dense class="closing-table">
      <thead>
        <tr class="header-row">
          <th class="text-left">{{ __("Payment Type") }}</th>
          <th class="text-right">{{ __("Closing Amount") }}</th>
          <th class="text-right">{{ __("Expected Amount") }}</th>
          <th class="text-right">{{ __("Difference") }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(values, method) in paymentMethods" :key="method" class="payment-item">
          <td class="text-left">{{ method }}</td>
          <td class="text-right">
            <v-text-field
              v-model.number="values.closing"
              single-line
              type="number"
              step="0.01"
              outlined
              dense
              hide-details
              class="amount-field"
              @change="$emit('update-payment', method, values.closing)"
            />
          </td>
          <td class="text-right">{{ currencySymbol(currency) }} {{ formtCurrency(values.expected || 0) }}</td>
          <td class="text-right">{{ currencySymbol(currency) }} {{ formtCurrency((values.expected || 0) - (values.closing || 0)) }}</td>
        </tr>
      </tbody>
    </v-simple-table>
  </template>
  
  <script>
  import format from "../../format";
  
  export default {
    name: "PaymentReconciliationTable",
    mixins: [format],
    props: {
      paymentMethods: { type: Object, required: true },
      currency: { type: String, required: true },
    },
  };
  </script>
  
  <style scoped>
  .closing-table {
    border: 1px solid #ddd;
  }
  
  .closing-table th,
  .closing-table td {
    padding: 8px;
    border-bottom: 1px solid #ddd;
    vertical-align: middle;
  }
  
  .closing-table th {
    background-color: #f5f5f5;
    font-weight: bold;
    border-bottom: 2px solid #000;
  }
  
  .closing-table tr:last-child td {
    border-bottom: none;
  }
  
  .closing-table .v-text-field.amount-field {
    max-width: 120px;
    margin: 6px auto;
  }
  
  .header-row {
    border-bottom: 2px solid #000;
  }
  </style>