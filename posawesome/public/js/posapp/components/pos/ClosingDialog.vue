<template>
  <v-row justify="center">
    <!-- Closing POS Shift Dialog -->
    <v-dialog v-model="closingDialog" max-width="900px" persistent>
      <v-card>
        <v-card-title class="pa-4">
          <span class="headline primary--text text-2xl font-medium">{{ __("Closing POS Shift") }}</span>
        </v-card-title>
        <v-card-text class="pa-6">
          <v-progress-circular v-if="loading" indeterminate color="primary" />
          <payment-reconciliation-table
            v-else-if="Object.keys(paymentMethods).length > 0"
            :payment-methods="paymentMethods"
            :currency="pos_profile.currency"
            :hide-expected-amount="pos_profile.hide_expected_amount"
            @update-payment="updatePayment"
          />
          <!-- Fallback table for debugging -->
          <v-simple-table v-else-if="Object.keys(paymentMethods).length > 0" class="fallback-table">
            <thead>
              <tr>
                <th class="text-left">{{ __("Payment Type") }}</th>
                <th class="text-right">{{ __("Closing Amount") }}</th>
                <th v-if="!pos_profile.hide_expected_amount" class="text-right">{{ __("Expected Amount") }}</th>
                <th v-if="!pos_profile.hide_expected_amount" class="text-right">{{ __("Excess") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(values, method) in paymentMethods" :key="method">
                <td class="text-left">{{ method }}</td>
                <td class="text-right">
                  {{ currencySymbol(pos_profile.currency) }} {{ formatCurrency(values.closing || 0) }}
                </td>
                <td v-if="!pos_profile.hide_expected_amount" class="text-right">
                  {{ currencySymbol(pos_profile.currency) }} {{ formatCurrency(values.expected || 0) }}
                </td>
                <td v-if="!pos_profile.hide_expected_amount" class="text-right">
                  {{ currencySymbol(pos_profile.currency) }}
                  {{ formatCurrency((values.closing != null ? values.closing : 0) - (values.expected || 0)) }}
                </td>
              </tr>
            </tbody>
          </v-simple-table>
          <div v-else class="text-center text-red-500">
            {{ __("No payment methods available. Error:") }} {{ errorMessage || __("Unknown error") }}
          </div>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn
            color="error"
            dark
            @click="close_dialog"
            class="px-6 min-w-[100px] rounded-lg text-base font-medium"
          >
            {{ __("Close") }}
          </v-btn>
          <v-btn
            color="success"
            dark
            @click="handleSubmit"
            class="px-6 min-w-[100px] rounded-lg text-base font-medium"
            :disabled="loading || Object.keys(paymentMethods).length === 0"
          >
            {{ __("Submit") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Daily Report Component (Hidden, used for printing) -->
    <daily-report
      ref="reportContent"
      :pos-profile="pos_profile"
      :pay-data="{ payInTotal, payOutTotal, payInEntries, payOutEntries, remainingBalance }"
      :items-sold="itemsSold"
      :payment-methods="paymentMethods"
      :current-date="currentDate"
      :current-time="currentTime"
      v-show="false"
    />
  </v-row>
</template>

<script>
import { evntBus } from "../../bus";
import format from "../../format";
import PaymentReconciliationTable from "./PaymentReconciliationTable.vue";
import DailyReport from "./DailyReport.vue";

export default {
  name: "POSClosingDialog",
  mixins: [format],
  components: {
    PaymentReconciliationTable,
    DailyReport,
  },
  data: () => ({
    closingDialog: false,
    pos_profile: { currency: "KWD", hide_expected_amount: false },
    paymentMethods: {},
    payments_method_data: [],
    currentShift: null,
    user: frappe.session.user,
    itemsSold: [],
    payInTotal: 0,
    payOutTotal: 0,
    payInEntries: [],
    payOutEntries: [],
    remainingBalance: 0,
    totalSalesByMode: {},
    loading: false,
    errorMessage: null,
  }),
  computed: {
    currentDate() {
      const today = new Date();
      return `${today.getDate().toString().padStart(2, "0")}/${(today.getMonth() + 1)
        .toString()
        .padStart(2, "0")}/${today.getFullYear()}`;
    },
    currentTime() {
      return new Date().toLocaleTimeString();
    },
  },
  methods: {
    close_dialog() {
      this.closingDialog = false;
      evntBus.$emit("close_closing_dialog");
    },
    updatePayment(method, value) {
      if (this.paymentMethods[method]) {
        Vue.set(this.paymentMethods[method], "closing", parseFloat(value) || 0);
        console.log(
          `POSClosingDialog.vue updated ${method} - closing: ${this.paymentMethods[method].closing}, expected: ${
            this.paymentMethods[method].expected
          }`
        );
      } else {
        console.warn(`POSClosingDialog.vue method ${method} not found in paymentMethods`);
      }
    },
    async fetchPaymentMethods() {
      try {
        this.loading = true;
        const response = await frappe.call({
          method: "posawesome.posawesome.api.posapp.get_opening_dialog_data",
          args: {},
        });

        if (response.message?.payments_method) {
          this.payments_method_data = response.message.payments_method;
          console.log("POSClosingDialog.vue fetched payment methods data:", this.payments_method_data);
        } else {
          console.error("POSClosingDialog.vue no payment methods returned from backend");
          this.errorMessage = __("No payment methods data received from server");
        }
      } catch (error) {
        console.error("POSClosingDialog.vue error fetching payment methods:", error);
        this.errorMessage =
          __("Error loading payment methods: ") + (error.message || __("Unknown error"));
      } finally {
        this.loading = false;
      }
    },
    updatePaymentMethods() {
      this.paymentMethods = {};
      if (this.payments_method_data && this.payments_method_data.length > 0) {
        this.payments_method_data.forEach((element) => {
          if (element.parent === this.pos_profile.name) {
            Vue.set(this.paymentMethods, element.mode_of_payment, {
              closing: 0,
              expected: this.totalSalesByMode[element.mode_of_payment] || 0,
              currency: element.currency,
            });
          }
        });
      } else {
        console.warn("POSClosingDialog.vue no payment methods data available to initialize");
        this.errorMessage = __("No payment methods data available");
      }
      console.log("POSClosingDialog.vue initialized paymentMethods:", this.paymentMethods);
    },
    async fetchTotalSalesByMode(openingShift) {
      try {
        this.loading = true;
        const invoices = await frappe.call({
          method: "posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.get_pos_invoices",
          args: { pos_opening_shift: openingShift },
        });

        const paymentTotals = {};
        if (invoices.message && Array.isArray(invoices.message)) {
          invoices.message.forEach((invoice) => {
            invoice.payments.forEach((payment) => {
              const mode = payment.mode_of_payment;
              paymentTotals[mode] = (paymentTotals[mode] || 0) + (payment.amount || 0);
            });
          });
        } else {
          console.warn("POSClosingDialog.vue invalid invoice data from get_pos_invoices:", invoices.message);
        }

        this.totalSalesByMode = paymentTotals;
        console.log("POSClosingDialog.vue total Sales by Mode:", this.totalSalesByMode);
      } catch (err) {
        console.error("POSClosingDialog.vue error fetching total sales by mode:", err);
        this.errorMessage =
          __("Error fetching sales data: ") + (err.message || __("Unknown error"));
      } finally {
        this.loading = false;
      }
    },
    async fetchAllSalesData(openingShift) {
      try {
        this.loading = true;
        const invoices = await frappe.call({
          method: "posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.get_pos_invoices",
          args: { pos_opening_shift: openingShift },
        });

        const itemTotals = {};
        if (invoices.message && Array.isArray(invoices.message)) {
          invoices.message.forEach((invoice) => {
            invoice.items.forEach((item) => {
              const key = item.item_name;
              if (itemTotals[key]) {
                itemTotals[key].qty += item.qty;
                itemTotals[key].amount += item.amount;
              } else {
                itemTotals[key] = {
                  item_name: item.item_name,
                  qty: item.qty,
                  amount: item.amount,
                };
              }
            });
          });
        } else {
          console.warn("POSClosingDialog.vue invalid invoice data for items:", invoices.message);
        }

        this.itemsSold = Object.values(itemTotals);
        console.log("POSClosingDialog.vue aggregated Items Sold:", this.itemsSold);
      } catch (err) {
        console.error("POSClosingDialog.vue error fetching all sales data:", err);
        this.errorMessage =
          __("Error fetching sales items: ") + (err.message || __("Unknown error"));
      } finally {
        this.loading = false;
      }
    },
    async handleSubmit() {
      try {
        if (!this.pos_profile || !this.pos_profile.name) {
          throw new Error(__("POS Profile is not defined. Please register a POS Profile."));
        }

        if (!Object.keys(this.paymentMethods).length) {
          throw new Error(__("No payment methods available. Please check POS Profile."));
        }

        let openingShift;
        try {
          const shiftResponse = await frappe.call({
            method: "frappe.client.get_list",
            args: {
              doctype: "POS Opening Shift",
              filters: [["pos_profile", "=", this.pos_profile.name], ["status", "=", "Open"]],
              fields: ["name"],
              order_by: "creation desc",
              limit_page_length: 1,
            },
          });
          openingShift = shiftResponse.message?.[0]?.name;
          if (!openingShift) {
            throw new Error(__("No open shift found for this POS Profile."));
          }
        } catch (err) {
          console.error("POSClosingDialog.vue error fetching opening shift:", err);
          throw new Error(
            __("Error fetching open shift: ") + (err.message || __("Unknown error"))
          );
        }

        await this.fetchTotalSalesByMode(openingShift);
        await this.fetchAllSalesData(openingShift);

        const finalPaymentMethods = JSON.parse(JSON.stringify(this.paymentMethods));
        console.log("POSClosingDialog.vue final Payment Methods before submission:", finalPaymentMethods);

        Object.keys(finalPaymentMethods).forEach((method) => {
          finalPaymentMethods[method].expected = this.totalSalesByMode[method] || 0;
        });

        const closingData = {
          doctype: "POS Closing Shift",
          pos_profile: this.pos_profile.name,
          user: this.user,
          pos_opening_shift: openingShift,
          period_end_date: frappe.datetime.now_datetime(),
          payment_reconciliation: Object.entries(finalPaymentMethods).map(([method, values]) => ({
            mode_of_payment: method,
            opening_amount: 0,
            expected_amount: parseFloat(values.expected) || 0,
            closing_amount: parseFloat(values.closing) || 0,
          })),
        };

        const closingDataString = JSON.stringify(closingData);
        console.log("POSClosingDialog.vue closing Data sent to server:", closingDataString);
        console.log("POSClosingDialog.vue closing Data size:", new TextEncoder().encode(closingDataString).length, "bytes");
        evntBus.$emit("submit_closing_pos", closingData);

        // Use fetch instead of frappe.call to avoid Expect: 100-continue
        const response = await fetch("/api/method/posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.submit_closing_shift", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Frappe-CSRF-Token": frappe.csrf_token || "",
          },
          credentials: "include",
          body: JSON.stringify({ closing_shift: closingDataString }),
        });

        let closeResponse;
        try {
          closeResponse = await response.json();
        } catch (jsonErr) {
          console.error("POSClosingDialog.vue error parsing JSON response:", jsonErr, { status: response.status, statusText: response.statusText });
          throw new Error(__("Invalid server response: Failed to parse JSON"));
        }

        console.log("POSClosingDialog.vue close Shift Response:", JSON.stringify(closeResponse, null, 2));

        if (!response.ok) {
          let errorMsg = `HTTP ${response.status}: ${response.statusText}`;
          if (response.status === 417) {
            errorMsg = __("Server rejected request (Expectation Failed). Please check server configuration or payload size.");
          } else if (response.status === 403) {
            errorMsg = __("Permission Denied: You lack the necessary permissions to close the shift.");
          } else if (response.status === 500) {
            errorMsg = __("Server Error: Please contact the administrator.");
          }

          if (closeResponse.exc) {
            errorMsg = closeResponse.exc;
          } else if (closeResponse.message?.error) {
            errorMsg = closeResponse.message.error;
          } else if (closeResponse._server_messages) {
            try {
              const serverMessages = JSON.parse(closeResponse._server_messages);
              errorMsg = serverMessages.map(msg => JSON.parse(msg).message).join("; ");
            } catch (e) {
              errorMsg += "; Failed to parse server messages";
            }
          }

          throw new Error(errorMsg);
        }

        if (!closeResponse.message || !closeResponse.message.message) {
          throw new Error(closeResponse.message?.error || __("Unknown server error"));
        }

        evntBus.$emit("show_mesage", {
          text: __("POS Shift Closed"),
          color: "success",
        });

        this.paymentMethods = { ...finalPaymentMethods };
        console.log("POSClosingDialog.vue payment Methods for report:", this.paymentMethods);
        console.log("POSClosingDialog.vue payData for DailyReport:", {
          payInTotal: this.payInTotal,
          payOutTotal: this.payOutTotal,
          payInEntries: this.payInEntries,
          payOutEntries: this.payOutEntries,
          remainingBalance: this.remainingBalance,
        });
        await this.printDailyReport();

        this.closingDialog = false;
        evntBus.$emit("shift_closed");
        await this.logoutAndRedirect();
      } catch (err) {
        console.error("POSClosingDialog.vue error in submit process:", {
          message: err.message,
          stack: err.stack,
          response: err.status ? {
            status: err.status,
            statusText: err.statusText,
            responseText: err.responseText,
          } : null,
        });
        let errorMessage = err.message || __("An unexpected error occurred");
        if (err.status === 417) {
          errorMessage = __("Expectation Failed: Server rejected the request. Try again or contact support.");
        } else if (err.status === 403) {
          errorMessage = __("Permission Denied: You lack the necessary permissions to close the shift.");
        } else if (err.status === 500) {
          errorMessage = __("Server Error: Please contact the administrator.");
        }
        this.errorMessage = __("Error submitting shift: ") + errorMessage;
        frappe.msgprint({
          title: __("Error"),
          indicator: "red",
          message: this.errorMessage,
        });

        try {
          console.log("POSClosingDialog.vue payData for DailyReport (error case):", {
            payInTotal: this.payInTotal,
            payOutTotal: this.payOutTotal,
            payInEntries: this.payInEntries,
            payOutEntries: this.payOutEntries,
            remainingBalance: this.remainingBalance,
          });
          await this.printDailyReport();
        } catch (reportErr) {
          console.error("POSClosingDialog.vue error printing report after failure:", {
            message: reportErr.message,
            stack: reportErr.stack,
          });
          frappe.msgprint({
            title: __("Error"),
            indicator: "red",
            message: __("Failed to print daily report: ") + (reportErr.message || __("Unknown error")),
          });
        }

        this.closingDialog = false;
        await this.logoutAndRedirect();
      }
    },
    async printDailyReport() {
      try {
        await this.$nextTick();
        console.log("POSClosingDialog.vue payment Methods at print time:", this.paymentMethods);
        console.log("POSClosingDialog.vue payData at print time:", {
          payInTotal: this.payInTotal,
          payOutTotal: this.payOutTotal,
          payInEntries: this.payInEntries,
          payOutEntries: this.payOutEntries,
          remainingBalance: this.remainingBalance,
        });
        if (!this.$refs.reportContent || typeof this.$refs.reportContent.getPrintContent !== "function") {
          throw new Error(__("Daily Report component or getPrintContent method is not available"));
        }
        const printContent = await this.$refs.reportContent.getPrintContent();
        if (!printContent || typeof printContent !== "string" || printContent.trim() === "") {
          throw new Error(__("No content generated for daily report"));
        }
        console.log("POSClosingDialog.vue printContent length:", printContent.length);
        const printWindow = window.open("", "_blank");
        if (!printWindow) {
          throw new Error(__("Failed to open print window. Please allow pop-ups for this site."));
        }
        printWindow.document.write(printContent);
        printWindow.document.close();
        printWindow.focus();
        printWindow.print();
        printWindow.close();
      } catch (err) {
        console.error("POSClosingDialog.vue error printing daily report:", {
          message: err.message,
          stack: err.stack,
        });
        throw err;
      }
    },
    async logoutAndRedirect() {
      try {
        const response = await fetch("/api/method/logout", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Frappe-CSRF-Token": frappe.csrf_token || "",
          },
          credentials: "include",
        });

        if (!response.ok) {
          console.warn("POSClosingDialog.vue logout request failed with status:", response.status);
        }
      } catch (error) {
        console.error("POSClosingDialog.vue logout error:", error);
      } finally {
        localStorage.clear();
        sessionStorage.clear();
        document.cookie.split(";").forEach((c) => {
          document.cookie = c
            .replace(/^ +/, "")
            .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
        });
        window.location.replace("/login?nocache=" + Date.now());
      }
    },
  },
  created() {
    evntBus.$on("open_ClosingDialog", async (data) => {
      this.loading = true;
      this.errorMessage = null;

      if (data?.payment_reconciliation) {
        data.payment_reconciliation.forEach((p) => {
          if (this.paymentMethods[p.mode_of_payment]) {
            this.paymentMethods[p.mode_of_payment].closing = parseFloat(p.closing_amount || 0);
            this.paymentMethods[p.mode_of_payment].expected = parseFloat(p.expected_amount || 0);
            console.log(
              `POSClosingDialog.vue loaded ${p.mode_of_payment} - closing: ${p.closing_amount}, expected: ${p.expected_amount}`
            );
          }
        });
        this.currentShift = data.name;
      }

      let openingShift;
      try {
        const shiftResponse = await frappe.call({
          method: "frappe.client.get_list",
          args: {
            doctype: "POS Opening Shift",
            filters: [["pos_profile", "=", this.pos_profile.name], ["status", "=", "Open"]],
            fields: ["name"],
            order_by: "creation desc",
            limit_page_length: 1,
          },
        });
        openingShift = shiftResponse.message?.[0]?.name;
        if (!openingShift) {
          throw new Error(__("No open shift found for this POS Profile."));
        }
        this.currentShift = openingShift;
      } catch (err) {
        console.error("POSClosingDialog.vue error fetching opening shift in created:", err);
        this.errorMessage =
          __("Error fetching open shift: ") + (err.message || __("Unknown error"));
        this.loading = false;
        this.closingDialog = true;
        return;
      }

      try {
        await this.fetchPaymentMethods();
        await this.fetchTotalSalesByMode(openingShift);
        await this.fetchAllSalesData(openingShift);

        this.updatePaymentMethods();
        console.log("POSClosingDialog.vue payment Methods before dialog display:", this.paymentMethods);

        if (Object.keys(this.paymentMethods).length === 0) {
          this.errorMessage = __("No payment methods initialized");
        }
      } catch (err) {
        console.error("POSClosingDialog.vue error preparing dialog data:", err);
        this.errorMessage = __("Error preparing dialog: ") + (err.message || __("Unknown error"));
      } finally {
        this.loading = false;
        this.closingDialog = true;
        console.log("POSClosingDialog.vue dialog opened with paymentMethods:", this.paymentMethods);
        console.log("POSClosingDialog.vue initial payData:", {
          payInTotal: this.payInTotal,
          payOutTotal: this.payOutTotal,
          payInEntries: this.payInEntries,
          payOutEntries: this.payOutEntries,
          remainingBalance: this.remainingBalance,
        });
      }
    });

    evntBus.$on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile || { currency: "KWD", hide_expected_amount: false };
      console.log("POSClosingDialog.vue registered POS Profile:", this.pos_profile);
    });

    evntBus.$on("update-piti-totals", (data) => {
      console.log("POSClosingDialog.vue received update-piti-totals:", data);
      this.payInTotal = parseFloat(data.payInTotal || 0);
      this.payOutTotal = parseFloat(data.payOutTotal || 0);
      this.payInEntries = data.payInEntries || [];
      this.payOutEntries = data.payOutEntries || [];
      Vue.set(this, "remainingBalance", parseFloat(data.remainingBalance || 0));
      console.log("POSClosingDialog.vue updated payData:", {
        payInTotal: this.payInTotal,
        payOutTotal: this.payOutTotal,
        payInEntries: this.payInEntries,
        payOutEntries: this.payOutEntries,
        remainingBalance: this.remainingBalance,
      });
    });
  },
  beforeDestroy() {
    evntBus.$off("open_ClosingDialog");
    evntBus.$off("register_pos_profile");
    evntBus.$off("update-piti-totals");
    console.log("POSClosingDialog.vue beforeDestroy: Unregistered event listeners");
  },
};
</script>

<style scoped>
.v-dialog .v-card {
  border-radius: 0.75rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.v-card-title {
  font-size: 1.5rem;
  font-weight: 500;
}

.v-card-text {
  padding: 1.5rem;
  min-height: 200px;
}

.v-card-actions {
  padding: 1rem;
}

.v-btn {
  min-width: 4rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
}

.text-red-500 {
  color: #ef4444;
}
</style>