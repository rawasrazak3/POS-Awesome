<template>
  <v-row justify="center">
    <!-- Closing POS Shift Dialog -->
    <v-dialog v-model="closingDialog" max-width="900px" persistent>
      <v-card>
        <v-card-title class="pa-4">
          <span class="headline primary--text text-2xl font-medium">{{ __("Closing POS Shift") }}</span>
        </v-card-title>
        <v-card-text class="pa-6">
          <payment-reconciliation-table
            :payment-methods="paymentMethods"
            :currency="pos_profile.currency"
            @update-payment="updatePayment"
          />
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer />
          <v-btn color="error" dark @click="close_dialog" class="px-6 min-w-[100px] rounded-lg text-base font-medium">{{ __("Close") }}</v-btn>
          <v-btn color="success" dark @click="closeShiftAndLogout" class="px-6 min-w-[100px] rounded-lg text-base font-medium">{{ __("Submit") }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Daily Report Dialog -->
    <v-dialog v-model="reportDialog" fullscreen hide-overlay transition="dialog-bottom-transition">
      <v-card>
        <v-toolbar dark color="primary">
          <v-btn icon dark @click="reportDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>Daily Report - VR Mania</v-toolbar-title>
          <v-spacer />
          <v-toolbar-items>
            <v-btn dark text @click="printReportAndLogout">
              <v-icon left>mdi-printer</v-icon>
              Print
            </v-btn>
          </v-toolbar-items>
        </v-toolbar>
        <v-card-text>
          <daily-report
            ref="reportContent"
            :pos-profile="pos_profile"
            :pay-data="{ payInTotal, payOutTotal, payInEntries, payOutEntries }"
            :items-sold="itemsSold"
            :payment-methods="paymentMethods"
            :current-date="currentDate"
            :current-time="currentTime"
          />
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Opening Shift Dialog (kept but not triggered) -->
    <opening-dialog
      :dialog="openShiftDialog"
      @shift-opened="handleShiftOpened"
    />
  </v-row>
</template>

<script>
import { evntBus } from "../../bus";
import format from "../../format";
import PaymentReconciliationTable from "./PaymentReconciliationTable.vue";
import DailyReport from "./DailyReport.vue";
import OpeningDialog from "./OpeningDialog.vue";

export default {
  name: "POSClosingDialog",
  mixins: [format],
  components: {
    PaymentReconciliationTable,
    DailyReport,
    OpeningDialog,
  },
  data: () => ({
    closingDialog: false,
    reportDialog: false,
    openShiftDialog: false,
    pos_profile: { currency: "KWD" },
    itemsSold: [],
    payInTotal: 0,
    payOutTotal: 0,
    payInEntries: [],
    payOutEntries: [],
    paymentMethods: {},
    payments_method_data: [],
    logged_out: false,
    last_invoice: "",
    currentShift: null,
  }),
  computed: {
    currentDate() {
      const today = new Date();
      return `${today.getDate().toString().padStart(2, "0")}/${(today.getMonth() + 1).toString().padStart(2, "0")}/${today.getFullYear()}`;
    },
    currentTime() {
      return new Date().toLocaleTimeString();
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
    totalItemsSold() {
      return this.itemsSold.reduce((sum, item) => sum + (item.amount || 0), 0);
    },
  },
  watch: {
    pos_profile: {
      handler(newVal) {
        if (newVal?.name) {
          this.fetchPaymentMethods();
        }
      },
      deep: true,
    },
  },
  methods: {
    close_dialog() {
      this.closingDialog = false;
      evntBus.$emit("close_closing_dialog");
    },
    updatePayment(method, value) {
      this.paymentMethods[method].closing = parseFloat(value) || 0;
    },
    async fetchPaymentMethods() {
      try {
        const response = await frappe.call({
          method: "posawesome.posawesome.api.posapp.get_opening_dialog_data",
          args: {},
        });

        if (response.message?.payments_method) {
          this.payments_method_data = response.message.payments_method;
          this.updatePaymentMethods();
        } else {
          console.error("No payment methods returned from backend");
          frappe.msgprint("Failed to load payment methods.");
        }
      } catch (error) {
        console.error("Error fetching payment methods:", error);
        frappe.msgprint("Error loading payment methods: " + (error.message || "Unknown error"));
      }
    },
    updatePaymentMethods() {
      this.paymentMethods = {};
      this.payments_method_data.forEach((element) => {
        if (element.parent === this.pos_profile.name) {
          this.paymentMethods[element.mode_of_payment] = {
            closing: 0,
            expected: 0,
            currency: element.currency,
          };
        }
      });
    },
    async closeShiftAndLogout() {
      if (!Object.keys(this.paymentMethods).length) {
        frappe.msgprint("No payment methods available. Please check POS Profile.");
        return;
      }

      const closingData = {
        payment_reconciliation: Object.entries(this.paymentMethods).map(([method, values]) => ({
          mode_of_payment: method,
          closing_amount: values.closing,
          expected_amount: values.expected,
        })),
        pos_profile: this.pos_profile.name,
        opening_shift: this.currentShift || this.pos_opening_shift,
      };

      evntBus.$emit("submit_closing_pos", closingData);

      try {
        const response = await frappe.call({
          method: "frappe.client.set_value",
          args: {
            doctype: "POS Profile",
            name: this.pos_profile.name,
            fieldname: "status",
            value: "Closed",
          },
        });

        if (response.message) {
          await this.fetchLastInvoice();
          this.closingDialog = false;
          this.reportDialog = true;
        }
      } catch (err) {
        console.error("Shift close error:", err);
        frappe.msgprint("Error closing shift: " + err.message);
      }
    },
    async fetchLastInvoice() {
      const response = await frappe.call({
        method: "frappe.client.get_list",
        args: {
          doctype: "Sales Invoice",
          fields: ["name"],
          order_by: "creation desc",
          limit_page_length: 1,
        },
      });

      if (response.message?.length) {
        this.last_invoice = response.message[0].name;
        await this.fetchItemsSold();
      }
    },
    async fetchItemsSold() {
      if (!this.last_invoice) return;

      const response = await frappe.call({
        method: "frappe.client.get",
        args: { doctype: "Sales Invoice", name: this.last_invoice },
      });

      if (response.message) {
        this.itemsSold = response.message.items.map(item => ({
          item_name: item.item_name,
          qty: item.qty,
          amount: item.amount,
        }));
      }
    },
    resetShiftData() {
      Object.values(this.paymentMethods).forEach(method => {
        method.closing = 0;
        method.expected = 0;
      });
      this.payInTotal = 0;
      this.payOutTotal = 0;
      this.payInEntries = [];
      this.payOutEntries = [];
      this.itemsSold = [];
      evntBus.$emit("shift_opened");
    },
    async printReportAndLogout() {
      this.$nextTick(async () => {
        const printWindow = window.open("", "_blank");
        printWindow.document.write(await this.$refs.reportContent.getPrintContent());
        printWindow.document.close();
        printWindow.focus();

        this.reportDialog = false;
        this.resetShiftData();

        try {
          const response = await fetch("/api/method/logout", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Frappe-CSRF-Token": frappe.csrf_token || "",
              "Cache-Control": "no-cache, no-store, must-revalidate",
              Pragma: "no-cache",
              Expires: "0",
            },
            credentials: "include",
          });

          if (response.ok) {
            localStorage.clear();
            sessionStorage.clear();
            document.cookie.split(";").forEach(c => {
              document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
            });
            window.location.replace("/login?nocache=" + Date.now());
          }
        } catch (error) {
          console.error("Logout error:", error);
          frappe.msgprint("Logout failed: " + error.message);
        }
      });
    },
    updatePitiTotals(data) {
      this.payInTotal += parseFloat(data.payInAmount || 0);
      this.payOutTotal += parseFloat(data.payOutAmount || 0);
      if (data.payInEntries) this.payInEntries = data.payInEntries;
      if (data.payOutEntries) this.payOutEntries = data.payOutEntries;
    },
    handleShiftOpened() {
      this.openShiftDialog = false;
      this.resetShiftData();
    },
  },
  created() {
    evntBus.$on("open_ClosingDialog", (data) => {
      if (data?.payment_reconciliation) {
        data.payment_reconciliation.forEach(p => {
          if (this.paymentMethods[p.mode_of_payment]) {
            this.paymentMethods[p.mode_of_payment].closing = parseFloat(p.closing_amount || 0);
            this.paymentMethods[p.mode_of_payment].expected = parseFloat(p.expected_amount || 0);
          }
        });
        this.currentShift = data.name;
      }
      this.closingDialog = true;
    });

    evntBus.$on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile || { currency: "KWD" };
    });

    evntBus.$on("update-piti-totals", this.updatePitiTotals);
  },
  beforeDestroy() {
    evntBus.$off("open_ClosingDialog");
    evntBus.$off("register_pos_profile");
    evntBus.$off("update-piti-totals");
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
</style>