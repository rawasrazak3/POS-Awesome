<template>
  <v-row justify="center">
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
                <td class="text-right">{{ formatCurrency(values.closing || 0) }}</td>
                <td v-if="!pos_profile.hide_expected_amount" class="text-right">
                  {{ formatCurrency(values.expected || 0) }}
                </td>
                <td v-if="!pos_profile.hide_expected_amount" class="text-right">
                  {{ formatCurrency((values.closing || 0) - (values.expected || 0)) }}
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
          <v-btn color="error" dark @click="close_dialog" class="px-6 min-w-[100px] rounded-lg text-base font-medium">
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
    <daily-report
      ref="reportContent"
      :pos-profile="pos_profile"
      :pay-data="{ payInTotal, payOutTotal, payInEntries, payOutEntries }"
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
  components: { PaymentReconciliationTable, DailyReport },
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
    totalSalesByMode: {},
    loading: false,
    errorMessage: null,
    isPrinting: false,
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
      this.logoutAndRedirect();
    },
    updatePayment(method, value) {
      if (this.paymentMethods[method]) {
        Vue.set(this.paymentMethods[method], "closing", parseFloat(value) || 0);
      } else {
        console.warn(`Method ${method} not found`);
      }
    },
    async fetchPaymentMethods() {
      try {
        this.loading = true;
        const response = await frappe.call({
          method: "posawesome.posawesome.api.posapp.get_opening_dialog_data",
          args: {},
        });
        this.payments_method_data = response.message?.payments_method || [];
        if (!this.payments_method_data.length) {
          this.errorMessage = __("No payment methods data received");
        }
      } catch (error) {
        this.errorMessage = __("Error loading payment methods: ") + (error.message || __("Unknown error"));
      } finally {
        this.loading = false;
      }
    },
    updatePaymentMethods() {
      this.paymentMethods = {};
      this.payments_method_data.forEach((element) => {
        if (element.parent === this.pos_profile.name) {
          Vue.set(this.paymentMethods, element.mode_of_payment, {
            closing: null,
            expected: this.totalSalesByMode[element.mode_of_payment] || 0,
            currency: element.currency,
          });
        }
      });
      if (!Object.keys(this.paymentMethods).length) {
        this.errorMessage = __("No payment methods initialized");
      }
    },
    async fetchTotalSalesByMode(openingShift) {
      try {
        this.loading = true;
        const invoices = await frappe.call({
          method: "posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.get_pos_invoices",
          args: { pos_opening_shift: openingShift },
        });
        const paymentTotals = {};
        (invoices.message || []).forEach((invoice) => {
          invoice.payments.forEach((payment) => {
            paymentTotals[payment.mode_of_payment] =
              (paymentTotals[payment.mode_of_payment] || 0) + (payment.amount || 0);
          });
        });
        this.totalSalesByMode = paymentTotals;
      } catch (err) {
        this.errorMessage = __("Error fetching sales data: ") + (err.message || __("Unknown error"));
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
        (invoices.message || []).forEach((invoice) => {
          invoice.items.forEach((item) => {
            const key = item.item_name;
            itemTotals[key] = itemTotals[key] || { item_name: item.item_name, qty: 0, amount: 0 };
            itemTotals[key].qty += item.qty;
            itemTotals[key].amount += item.amount;
          });
        });
        this.itemsSold = Object.values(itemTotals);
      } catch (err) {
        this.errorMessage = __("Error fetching sales items: ") + (err.message || __("Unknown error"));
      } finally {
        this.loading = false;
      }
    },
    async handleSubmit() {
      try {
        this.loading = true;
        this.errorMessage = null;

        if (!this.pos_profile?.name) {
          throw new Error(__("POS Profile is not defined"));
        }
        if (!Object.keys(this.paymentMethods).length) {
          throw new Error(__("No payment methods available"));
        }

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
        const openingShift = shiftResponse.message?.[0]?.name;
        if (!openingShift) {
          throw new Error(__("No open shift found"));
        }

        await Promise.all([
          this.fetchTotalSalesByMode(openingShift),
          this.fetchAllSalesData(openingShift),
        ]);

        const finalPaymentMethods = JSON.parse(JSON.stringify(this.paymentMethods));
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
            expected_amount: values.expected || 0,
            closing_amount: values.closing || 0,
          })),
        };

        const closeResponse = await frappe.call({
          method: "posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.submit_closing_shift",
          args: { closing_shift: JSON.stringify(closingData) },
        });

        if (!closeResponse.message) {
          throw new Error(closeResponse.exc || __("Failed to submit POS Closing Shift"));
        }

        this.paymentMethods = { ...finalPaymentMethods };
        frappe.msgprint({ title: __("Success"), indicator: "green", message: __("POS Shift Closed Successfully") });

        await this.printDailyReport();
        await this.logoutAndRedirect();
      } catch (err) {
        this.errorMessage = __("Error submitting shift: ") + (err.message || __("Unknown error"));
        frappe.msgprint({ title: __("Error"), indicator: "red", message: this.errorMessage });
      } finally {
        this.loading = false;
        this.closingDialog = false;
      }
    },
    async printDailyReport() {
      if (this.isPrinting) {
        console.log("Print attempt blocked: already printing");
        return Promise.resolve();
      }
      this.isPrinting = true;
      try {
        console.log("Starting printDailyReport");
        await this.$nextTick();
        if (!this.$refs.reportContent?.getPrintContent) {
          throw new Error(__("Daily Report component or getPrintContent method is not available"));
        }
        const printContent = await this.$refs.reportContent.getPrintContent();
        if (!printContent) {
          throw new Error(__("No content generated for daily report"));
        }
        const printWindow = window.open("", "_blank");
        if (!printWindow) {
          throw new Error(__("Unable to open print window. Please allow pop-ups."));
        }
        console.log("Print window opened");
        printWindow.document.write(printContent);
        printWindow.document.close();
        return new Promise((resolve, reject) => {
          printWindow.onload = () => {
            console.log("Print window content loaded");
            printWindow.focus();
            setTimeout(() => {
              console.log("Triggering print");
              printWindow.print();
              printWindow.onafterprint = () => {
                console.log("Print job completed or canceled");
                printWindow.close();
                resolve();
              };
              // Fallback for browsers without reliable onafterprint
              setTimeout(() => {
                if (!printWindow.closed) {
                  console.log("Closing print window via timeout");
                  printWindow.close();
                }
                resolve();
              },); // Close after 3s if onafterprint doesn't fire
            },); // Increased delay for rendering
          };
          // Handle window load failure
          setTimeout(() => {
            if (!printWindow.document.readyState === "complete") {
              console.error("Print window failed to load");
              printWindow.close();
              reject(new Error("Print window failed to load"));
            }
          }, 1000);
        });
      } catch (err) {
        console.error("Error printing daily report:", err);
        frappe.msgprint({
          title: __("Error"),
          indicator: "red",
          message: __("Failed to print daily report: ") + (err.message || __("Unknown error")),
        });
        throw err;
      } finally {
        this.isPrinting = false;
        console.log("Print process completed");
      }
    },
    async logoutAndRedirect() {
      try {
        const response = await fetch("/api/method/logout", {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-Frappe-CSRF-Token": frappe.csrf_token || "" },
          credentials: "include",
        });
        if (!response.ok) {
          frappe.msgprint({
            title: __("Warning"),
            indicator: "orange",
            message: __("Logout request failed, but proceeding with redirect"),
          });
        }
      } catch (error) {
        frappe.msgprint({
          title: __("Error"),
          indicator: "red",
          message: __("Error during logout: ") + (error.message || __("Unknown error")),
        });
      } finally {
        localStorage.clear();
        sessionStorage.clear();
        document.cookie.split(";").forEach((c) => {
          document.cookie = c
            .replace(/^ +/, "")
            .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
        });
        window.location.href = `/login?nocache=${Date.now()}`;
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
            Vue.set(this.paymentMethods[p.mode_of_payment], "closing", parseFloat(p.closing_amount || 0));
            Vue.set(this.paymentMethods[p.mode_of_payment], "expected", parseFloat(p.expected_amount || 0));
          }
        });
        this.currentShift = data.name;
      }

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
      const openingShift = shiftResponse.message?.[0]?.name;
      if (!openingShift) {
        this.errorMessage = __("No open shift found");
        this.loading = false;
        this.closingDialog = true;
        return;
      }
      this.currentShift = openingShift;

      try {
        await this.fetchPaymentMethods();
        await Promise.all([
          this.fetchTotalSalesByMode(openingShift),
          this.fetchAllSalesData(openingShift),
        ]);
        this.updatePaymentMethods();
      } catch (err) {
        this.errorMessage = __("Error preparing dialog: ") + (err.message || __("Unknown error"));
      } finally {
        this.loading = false;
        this.closingDialog = true;
      }
    });

    evntBus.$on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile || { currency: "KWD", hide_expected_amount: false };
    });

    evntBus.$on("update-piti-totals", (data) => {
      this.payInTotal += parseFloat(data.payInAmount || 0);
      this.payOutTotal += parseFloat(data.payOutAmount || 0);
      if (data.payInEntries) this.payInEntries = data.payInEntries;
      if (data.payOutEntries) this.payOutEntries = data.payOutEntries;
    });
  },
  beforeDestroy() {
    evntBus.$off("open_ClosingDialog");
    evntBus.$off("register_pos_profile");
    evntBus.$off("update-piti-totals");
  },
};
</script>

<style scoped>
.v-dialog .v-card { border-radius: 0.75rem; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2); }
.v-card-title { font-size: 1.5rem; font-weight: 500; }
.v-card-text { padding: 1.5rem; min-height: 200px; }
.v-card-actions { padding: 1rem; }
.v-btn { min-width: 4rem; border-radius: 0.5rem; font-size: 1rem; font-weight: 500; }
.text-red-500 { color: #ef4444; }
</style>