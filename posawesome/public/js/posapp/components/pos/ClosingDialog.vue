<template>
  <v-row justify="center">
    <!-- Closing POS Shift Dialog -->
    <v-dialog v-model="closingDialog" max-width="900px" persistent>
      <v-card>
        <v-card-title>
          <span class="headline primary--text">{{
            __("Closing POS Shift")
          }}</span>
        </v-card-title>
        <v-card-text class="pa-4">
          <v-container>
            <v-row>
              <v-col cols="12">
                <div class="payment-list">
                  <v-simple-table dense class="closing-table">
                    <template v-slot:default>
                      <thead>
                        <tr class="header-row">
                          <th class="text-left">{{ __("Payment Type") }}</th>
                          <th class="text-right">{{ __("Closing Amount") }}</th>
                          <th class="text-right">
                            {{ __("Expected Amount") }}
                          </th>
                          <th class="text-right">{{ __("Difference") }}</th>
                        </tr>
                      </thead>
                      <tbody>
                        <!-- Cash -->
                        <tr class="payment-item">
                          <td class="text-left">Cash</td>
                          <td class="text-right">
                            <v-text-field
                              v-model.number="cashClosing"
                              single-line
                              type="number"
                              step="0.01"
                              outlined
                              dense
                              hide-details
                              class="amount-field"
                              @change="updatePayment('Cash', cashClosing)"
                            ></v-text-field>
                          </td>
                          <td class="text-right">
                            {{ currencySymbol(pos_profile.currency) }}
                            {{ formtCurrency(cashExpected || 0) }}
                          </td>
                          <td class="text-right">
                            {{ currencySymbol(pos_profile.currency) }}
                            {{
                              formtCurrency(
                                (cashExpected || 0) - (cashClosing || 0)
                              )
                            }}
                          </td>
                        </tr>
                        <!-- KNET -->
                        <tr class="payment-item">
                          <td class="text-left">KNET</td>
                          <td class="text-right">
                            <v-text-field
                              v-model.number="knetClosing"
                              single-line
                              type="number"
                              step="0.01"
                              outlined
                              dense
                              hide-details
                              class="amount-field"
                              @change="updatePayment('KNET', knetClosing)"
                            ></v-text-field>
                          </td>
                          <td class="text-right">
                            {{ currencySymbol(pos_profile.currency) }}
                            {{ formtCurrency(knetExpected || 0) }}
                          </td>
                          <td class="text-right">
                            {{ currencySymbol(pos_profile.currency) }}
                            {{
                              formtCurrency(
                                (knetExpected || 0) - (knetClosing || 0)
                              )
                            }}
                          </td>
                        </tr>
                        <!-- Icards -->
                        <tr class="payment-item">
                          <td class="text-left">Icards</td>
                          <td class="text-right">
                            <v-text-field
                              v-model.number="icardsClosing"
                              single-line
                              type="number"
                              step="0.01"
                              outlined
                              dense
                              hide-details
                              class="amount-field"
                              @change="updatePayment('Icards', icardsClosing)"
                            ></v-text-field>
                          </td>
                          <td class="text-right">
                            {{ currencySymbol(pos_profile.currency) }}
                            {{ formtCurrency(icardsExpected || 0) }}
                          </td>
                          <td class="text-right">
                            {{ currencySymbol(pos_profile.currency) }}
                            {{
                              formtCurrency(
                                (icardsExpected || 0) - (icardsClosing || 0)
                              )
                            }}
                          </td>
                        </tr>
                        <!-- Sheel -->
                        <tr class="payment-item">
                          <td class="text-left">Sheel</td>
                          <td class="text-right">
                            <v-text-field
                              v-model.number="sheelClosing"
                              single-line
                              type="number"
                              step="0.01"
                              outlined
                              dense
                              hide-details
                              class="amount-field"
                              @change="updatePayment('Sheel', sheelClosing)"
                            ></v-text-field>
                          </td>
                          <td class="text-right">
                            {{ currencySymbol(pos_profile.currency) }}
                            {{ formtCurrency(sheelExpected || 0) }}
                          </td>
                          <td class="text-right">
                            {{ currencySymbol(pos_profile.currency) }}
                            {{
                              formtCurrency(
                                (sheelExpected || 0) - (sheelClosing || 0)
                              )
                            }}
                          </td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </div>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" dark @click="close_dialog">{{
            __("Close")
          }}</v-btn>
          <v-btn color="success" dark @click="closeShiftAndShowReport">{{
            __("Submit")
          }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Daily Report Dialog -->
    <v-dialog
      v-model="reportDialog"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
    >
      <v-card>
        <v-toolbar dark color="primary">
          <v-btn icon dark @click="reportDialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>Daily Report - VR Mania</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-toolbar-items>
            <v-btn dark text @click="printReportAndLogout">
              <v-icon left>mdi-printer</v-icon>
              Print
            </v-btn>
          </v-toolbar-items>
        </v-toolbar>
        <v-card-text>
          <div class="report-preview" ref="reportContent">
            <div class="text-center mb-6">
              <h1>VR Mania Avenues</h1>
              <div class="subtitle">Daily Shift Report</div>
            </div>

            <v-row class="mb-4">
              <v-col cols="6">
                <div><strong>Date:</strong> {{ currentDate }}</div>
              </v-col>
              <v-col cols="6" class="text-right">
                <div><strong>Time:</strong> {{ currentTime }}</div>
              </v-col>
            </v-row>

            <div class="section-title">Pay Transactions</div>
            <v-simple-table class="mb-4">
              <template v-slot:default>
                <tbody>
                  <tr>
                    <td><strong>Pay In</strong></td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(payInTotal) }}
                    </td>
                  </tr>
                  <tr
                    v-for="(entry, index) in payInEntries"
                    :key="'payin-' + index"
                  >
                  <td><strong>Note</strong></td>

                    <td class="pl-6 text-right">{{ entry.note }}</td>
                  </tr>
                  <tr>
                    <td><strong>Pay Out</strong></td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(payOutTotal) }}
                    </td>
                  </tr>
                  <tr
                    v-for="(entry, index) in payOutEntries"
                    :key="'payout-' + index"
                  >
                    <td><strong>Note</strong></td>

                    <td class="pl-6 text-right">{{ entry.note }}</td>
                  </tr>
                  <tr>
                    <td><strong>Remaining</strong></td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(payInTotal - payOutTotal) }}
                    </td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>

            <div class="section-title">Items Sold</div>
            <v-simple-table class="mb-4">
              <template v-slot:default>
                <thead>
                  <tr>
                    <th>Item Name</th>
                    <th class="text-center">Qty</th>
                    <th class="text-right">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in itemsSold" :key="index">
                    <td>{{ item.item_name || item.name }}</td>
                    <td class="text-center">{{ item.qty || item.quantity }}</td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(item.amount) }}
                    </td>
                  </tr>
                  <tr>
                    <td colspan="2"><strong>Total Items Sold</strong></td>
                    <td class="text-right">
                      <strong
                        >{{ currencySymbol(pos_profile.currency) }}
                        {{ formtCurrency(totalItemsSold) }}</strong
                      >
                    </td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>

            <div class="section-title">Closing Shift Settlement</div>
            <v-simple-table class="mb-4 settlement-table">
              <template v-slot:default>
                <thead>
                  <tr>
                    <th class="text-left">Payment Type</th>
                    <th class="text-right">Closing Amount</th>
                    <th class="text-right">Expected Amount</th>
                    <th class="text-right">Difference</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td class="text-left">Cash</td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(cashClosing || 0) }}
                    </td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(cashExpected || 0) }}
                    </td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{
                        formtCurrency((cashExpected || 0) - (cashClosing || 0))
                      }}
                    </td>
                  </tr>
                  <tr>
                    <td class="text-left">KNET</td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(knetClosing || 0) }}
                    </td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(knetExpected || 0) }}
                    </td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{
                        formtCurrency((knetExpected || 0) - (knetClosing || 0))
                      }}
                    </td>
                  </tr>
                  <tr>
                    <td class="text-left">Icards</td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(icardsClosing || 0) }}
                    </td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(icardsExpected || 0) }}
                    </td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{
                        formtCurrency(
                          (icardsExpected || 0) - (icardsClosing || 0)
                        )
                      }}
                    </td>
                  </tr>
                  <tr>
                    <td class="text-left">Sheel</td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(sheelClosing || 0) }}
                    </td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{ formtCurrency(sheelExpected || 0) }}
                    </td>
                    <td class="text-right">
                      {{ currencySymbol(pos_profile.currency) }}
                      {{
                        formtCurrency(
                          (sheelExpected || 0) - (sheelClosing || 0)
                        )
                      }}
                    </td>
                  </tr>
                  <tr class="total-row">
                    <td class="text-left"><strong>Total</strong></td>
                    <td class="text-right">
                      <strong
                        >{{ currencySymbol(pos_profile.currency) }}
                        {{ formtCurrency(totalClosing) }}</strong
                      >
                    </td>
                    <td class="text-right">
                      <strong
                        >{{ currencySymbol(pos_profile.currency) }}
                        {{ formtCurrency(totalExpected) }}</strong
                      >
                    </td>
                    <td class="text-right">
                      <strong
                        >{{ currencySymbol(pos_profile.currency) }}
                        {{ formtCurrency(totalDifference) }}</strong
                      >
                    </td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>

            <div class="signature-section mt-8">
              <v-row>
                <v-col cols="6" class="text-center">
                  <div class="signature-line"></div>
                  <div>Cashier's Signature</div>
                </v-col>
                <v-col cols="6" class="text-center">
                  <div class="signature-line"></div>
                  <div>Manager's Signature</div>
                </v-col>
              </v-row>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from "../../bus";
import format from "../../format";

export default {
  mixins: [format],
  data: () => ({
    closingDialog: false,
    reportDialog: false,
    pos_profile: { currency: "KWD" },
    itemsSold: [],
    payInTotal: 0,
    payOutTotal: 0,
    payInEntries: [],
    payOutEntries: [],
    cashClosing: 0,
    cashExpected: 0,
    knetClosing: 0,
    knetExpected: 0,
    icardsClosing: 0,
    icardsExpected: 0,
    sheelClosing: 0,
    sheelExpected: 0,
    logged_out: false,
    last_invoice: "",
    paymentReconciliation: [],
    currentShift: null,
  }),
  computed: {
    currentDate() {
      const today = new Date();
      return `${today.getDate().toString().padStart(2, "0")}/${(
        today.getMonth() + 1
      )
        .toString()
        .padStart(2, "0")}/${today.getFullYear()}`;
    },
    currentTime() {
      const now = new Date();
      return now.toLocaleTimeString();
    },
    totalItemsSold() {
      return this.itemsSold.reduce((sum, item) => sum + (item.amount || 0), 0);
    },
    totalClosing() {
      return (
        (parseFloat(this.cashClosing) || 0) +
        (parseFloat(this.knetClosing) || 0) +
        (parseFloat(this.icardsClosing) || 0) +
        (parseFloat(this.sheelClosing) || 0)
      );
    },
    totalExpected() {
      return (
        (parseFloat(this.cashExpected) || 0) +
        (parseFloat(this.knetExpected) || 0) +
        (parseFloat(this.icardsExpected) || 0) +
        (parseFloat(this.sheelExpected) || 0)
      );
    },
    totalDifference() {
      return this.totalExpected - this.totalClosing;
    },
  },
  methods: {
    close_dialog() {
      this.closingDialog = false;
      evntBus.$emit("close_closing_dialog");
    },
    closeShiftAndShowReport() {
      const me = this;
      frappe.call({
        method: "frappe.client.set_value",
        args: {
          doctype: "POS Profile",
          name: this.pos_profile.name,
          fieldname: "status",
          value: "Closed",
        },
        callback: (response) => {
          if (response.message) {
            console.log("Shift closed successfully");
            me.fetchLastInvoice();
            me.closingDialog = false;
            me.reportDialog = true;
          } else {
            frappe.msgprint("Failed to close shift");
          }
        },
        error: (err) => {
          console.error("Shift close error:", err);
          frappe.msgprint("Error closing shift: " + err.message);
        },
      });
    },
    updatePayment(method, value) {
      switch (method) {
        case "Cash":
          this.cashClosing = parseFloat(value) || 0;
          break;
        case "KNET":
          this.knetClosing = parseFloat(value) || 0;
          break;
        case "Icards":
          this.icardsClosing = parseFloat(value) || 0;
          break;
        case "Sheel":
          this.sheelClosing = parseFloat(value) || 0;
          break;
      }
    },
    fetchLastInvoice() {
      frappe.call({
        method: "frappe.client.get_list",
        args: {
          doctype: "Sales Invoice",
          fields: ["name"],
          order_by: "creation desc",
          limit_page_length: 1,
        },
        callback: (response) => {
          if (response.message && response.message.length > 0) {
            this.last_invoice = response.message[0].name;
            console.log("Fetched last invoice:", this.last_invoice);
            this.fetchItemsSold();
          } else {
            console.warn("No Sales Invoices found");
            frappe.msgprint("No Sales Invoices found for this shift");
          }
        },
      });
    },
    fetchItemsSold() {
      if (this.last_invoice) {
        frappe.call({
          method: "frappe.client.get",
          args: {
            doctype: "Sales Invoice",
            name: this.last_invoice,
          },
          callback: (response) => {
            if (response.message) {
              this.itemsSold = response.message.items.map((item) => ({
                item_name: item.item_name,
                qty: item.qty,
                amount: item.amount,
              }));
              console.log("Items sold fetched:", this.itemsSold);
            }
          },
        });
      }
    },
    resetShiftData() {
      this.cashClosing = 0;
      this.cashExpected = 0;
      this.knetClosing = 0;
      this.knetExpected = 0;
      this.icardsClosing = 0;
      this.icardsExpected = 0;
      this.sheelClosing = 0;
      this.sheelExpected = 0;
      this.payInTotal = 0;
      this.payOutTotal = 0;
      this.payInEntries = [];
      this.payOutEntries = [];
      this.itemsSold = [];
      evntBus.$emit("shift_opened");
    },
    printReportAndLogout() {
      this.$nextTick(() => {
        const printContent = this.$refs.reportContent.innerHTML;
        const printWindow = window.open("", "_blank");

        printWindow.document.write(`
          <html>
            <head>
              <title>Daily Report - VR Mania</title>
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
                .total-row { font-weight: bold; background-color: #f9f9f9; }
                .signature-section { margin-top: 32px; }
                .signature-line { border-top: 1px solid #000; width: 200px; margin: 0 auto 10px; }
                .pl-6 { padding-left: 24px; }
              </style>
            </head>
            <body onload="window.print();">
              ${printContent}
            </body>
          </html>
        `);

        printWindow.document.close();
        printWindow.focus();

        // Close the report dialog
        this.reportDialog = false;

        // Reset shift data after printing
        this.resetShiftData();

        // Logout and redirect to login page
        const me = this;
        me.logged_out = true;
        fetch("/api/method/logout", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Frappe-CSRF-Token": frappe.csrf_token || "",
            "Cache-Control": "no-cache, no-store, must-revalidate",
            Pragma: "no-cache",
            Expires: "0",
          },
          credentials: "include",
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error("Logout failed with status: " + response.status);
            }
            return response.json();
          })
          .then(() => {
            localStorage.clear();
            sessionStorage.clear();
            document.cookie.split(";").forEach(function (c) {
              document.cookie = c
                .replace(/^ +/, "")
                .replace(
                  /=.*/,
                  "=;expires=" + new Date().toUTCString() + ";path=/"
                );
            });
            window.location.replace("/login?nocache=" + Date.now());
          })
          .catch((error) => {
            console.error("Logout error:", error);
            frappe.msgprint("Logout failed: " + error.message);
          });
      });
    },
    updatePitiTotals(data) {
      this.payInTotal += parseFloat(data.payInAmount || 0);
      this.payOutTotal += parseFloat(data.payOutAmount || 0);
      if (data.payInEntries) this.payInEntries = data.payInEntries;
      if (data.payOutEntries) this.payOutEntries = data.payOutEntries;
    },
    initializePaymentMethods() {
      const defaultMethods = ["Cash", "KNET", "Icards", "Sheel"];

      this.paymentReconciliation = defaultMethods.map((method) => ({
        mode_of_payment: method,
        closing_amount: 0,
        available_amount: 0,
        expected_amount: 0,
      }));
    },
  },
  created() {
    this.initializePaymentMethods();

    evntBus.$on("open_ClosingDialog", (data) => {
      if (data?.payment_reconciliation) {
        this.paymentReconciliation = data.payment_reconciliation.map((p) => ({
          mode_of_payment: p.mode_of_payment,
          closing_amount: parseFloat(p.closing_amount || 0),
          available_amount: parseFloat(p.available_amount || 0),
          expected_amount: parseFloat(p.expected_amount || 0),
        }));

        this.cashClosing =
          this.paymentReconciliation.find((p) => p.mode_of_payment === "Cash")
            ?.closing_amount || 0;
        this.cashExpected =
          this.paymentReconciliation.find((p) => p.mode_of_payment === "Cash")
            ?.expected_amount || 0;
        this.knetClosing =
          this.paymentReconciliation.find((p) => p.mode_of_payment === "KNET")
            ?.closing_amount || 0;
        this.knetExpected =
          this.paymentReconciliation.find((p) => p.mode_of_payment === "KNET")
            ?.expected_amount || 0;
        this.icardsClosing =
          this.paymentReconciliation.find((p) => p.mode_of_payment === "Icards")
            ?.closing_amount || 0;
        this.icardsExpected =
          this.paymentReconciliation.find((p) => p.mode_of_payment === "Icards")
            ?.expected_amount || 0;
        this.sheelClosing =
          this.paymentReconciliation.find((p) => p.mode_of_payment === "Sheel")
            ?.closing_amount || 0;
        this.sheelExpected =
          this.paymentReconciliation.find((p) => p.mode_of_payment === "Sheel")
            ?.expected_amount || 0;
      } else {
        this.initializePaymentMethods();
      }
      this.closingDialog = true;
    });

    evntBus.$on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile || { currency: "KWD" };
    });

    evntBus.$on("update-piti-totals", (data) => {
      this.updatePitiTotals(data);
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
.payment-list {
  width: 100%;
}

.closing-table {
  border: 1px solid #ddd;
}

.closing-table th,
.closing-table td {
  padding: 8px 8px; /* Increased vertical padding from 4px to 8px */
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

/* Reduced width for amount fields */
.closing-table .v-text-field.amount-field {
  max-width: 120px;
  margin: 6px auto;
  margin-left: 196px; /* Added vertical gap */
}

.closing-table .v-text-field {
  margin: 6px; /* Added vertical gap */
  padding: 0;
}

.header-row {
  border-bottom: 2px solid #000;
  margin-left: 112px;
}

.report-preview {
  background: white;
  color: black;
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  font-family: Arial, sans-serif;
}

.report-preview h1 {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 4px;
}

.subtitle {
  font-size: 16px;
  color: #555;
  margin-bottom: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin: 16px 0 8px 0;
  padding-bottom: 4px;
  border-bottom: 1px solid #ddd;
}

.settlement-table {
  border: 1px solid #ddd;
}

.settlement-table th,
.settlement-table td {
  padding: 8px;
  border: 1px solid #ddd;
}

.signature-line {
  border-top: 1px solid #000;
  width: 200px;
  margin: 0 auto 10px;
  height: 1px;
}

@media print {
  body * {
    visibility: hidden;
  }
  .report-preview,
  .report-preview * {
    visibility: visible;
  }
  .report-preview {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    padding: 20px;
  }
  .no-print {
    display: none !important;
  }
}
</style>
