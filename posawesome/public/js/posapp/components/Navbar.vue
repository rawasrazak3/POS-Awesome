```vue
<template>
  <nav>
    <v-app-bar app height="60" class="elevation-2">
      <v-app-bar-nav-icon
        @click.stop="drawer = !drawer"
        class="grey--text"
      ></v-app-bar-nav-icon>
      
      <v-img
        src="/assets/posawesome/js/posapp/components/pos/pos.png"
        alt="POS Awesome"
        max-width="32"
        class="mr-2"
        color="primary"
      ></v-img>
      
      <v-toolbar-title
        @click="go_desk"
        style="cursor: pointer"
        class="text-uppercase primary--text"
      >
        <span class="font-weight-light">pos</span>
        <span>awesome</span>
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <!-- Pay In and Pay Out buttons (now for Petty Cash) -->
      <v-btn class="pay-btn mr-2" color="success" @click="payInDialog = true">
        Pay In
      </v-btn>
      <v-btn class="pay-btn mr-2" color="error" @click="payOutDialog = true">
        Pay Out
      </v-btn>

      <v-btn style="cursor: unset" text color="primary">
        <span>{{ pos_profile.name }}</span>
      </v-btn>
      
      <v-menu offset-y>
        <template v-slot:activator="{ on, attrs }">
          <v-btn color="primary" dark text v-bind="attrs" v-on="on">
            Menu
          </v-btn>
        </template>
        <v-card class="mx-auto" max-width="300" tile>
          <v-list dense>
            <v-list-item-group v-model="menu_item" color="primary">
              <v-list-item
                @click="close_shift_dialog"
                v-if="!pos_profile.posa_hide_closing_shift && item == 0"
              >
                <v-list-item-icon>
                  <v-icon>mdi-content-save-move-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ __("Close Shift") }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
              
              <v-list-item
                @click="print_last_invoice"
                v-if="pos_profile.posa_allow_print_last_invoice && last_invoice"
              >
                <v-list-item-icon>
                  <v-icon>mdi-printer</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ __("Print Last Invoice") }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
              
              <v-divider class="my-0"></v-divider>
              
              <v-list-item @click="logOut">
                <v-list-item-icon>
                  <v-icon>mdi-logout</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ __("Logout") }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
              
              <v-list-item @click="go_about">
                <v-list-item-icon>
                  <v-icon>mdi-information-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ __("About") }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </v-card>
      </v-menu>
    </v-app-bar>

    <v-navigation-drawer
      v-model="drawer"
      :mini-variant.sync="mini"
      app
      class="primary margen-top"
      width="170"
    >
      <v-list dark>
        <v-list-item class="px-2">
          <v-list-item-avatar>
            <v-img :src="company_img"></v-img>
          </v-list-item-avatar>
          <v-list-item-title>{{ company }}</v-list-item-title>
          <v-btn icon @click.stop="mini = !mini">
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
        </v-list-item>
        <v-list-item-group v-model="item" color="white">
          <v-list-item
            v-for="item in items"
            :key="item.text"
            @click="changePage(item.text)"
          >
            <v-list-item-icon>
              <v-icon v-text="item.icon"></v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title v-text="item.text"></v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>

    <!-- Pay In Modal (now for Petty Cash Pay In) -->
    <v-dialog v-model="payInDialog" max-width="400">
      <v-card>
        <v-card-title class="headline success white--text">Petty Cash Pay In</v-card-title>
        <v-card-text class="pt-4">
          <v-textarea
            v-model="payInNote"
            label="Note"
            outlined
            rows="3"
            :rules="[rules.requiredNote]"
          ></v-textarea>
          <v-text-field
            v-model="payInAmount"
            label="Amount"
            type="number"
            outlined
            :rules="[rules.required, rules.positiveNumber]"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="payInDialog = false">Cancel</v-btn>
          <v-btn color="success" @click="submitPettyCashPayIn">Submit</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Pay Out Modal (now for Petty Cash Pay Out) -->
    <v-dialog v-model="payOutDialog" max-width="400">
      <v-card>
        <v-card-title class="headline error white--text">Petty Cash Pay Out</v-card-title>
        <v-card-text class="pt-4">
          <v-textarea
            v-model="payOutNote"
            label="Note"
            outlined
            rows="3"
            :rules="[rules.requiredNote]"
          ></v-textarea>
          <v-text-field
            v-model="payOutAmount"
            label="Amount"
            type="number"
            outlined
            :rules="[rules.required, rules.positiveNumber]"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="payOutDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="submitPettyCashPayOut">Submit</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snack" :timeout="5000" :color="snackColor" top class="top-center-snackbar">
      {{ snackText }}
    </v-snackbar>

    <v-dialog v-model="freeze" persistent max-width="290">
      <v-card>
        <v-card-title class="text-h5">
          {{ freezeTitle }}
        </v-card-title>
        <v-card-text>{{ freezeMsg }}</v-card-text>
      </v-card>
    </v-dialog>
  </nav>
</template>

<script>
import { evntBus } from "../bus";

export default {
  data() {
    return {
      drawer: false,
      mini: true,
      item: 0,
      items: [{ text: "POS", icon: "mdi-network-pos" }],
      menu_item: 0,
      snack: false,
      snackColor: "",
      snackText: "",
      company: "POS Awesome",
      company_img: "/assets/erpnext/images/erpnext-logo.svg",
      pos_profile: {},
      freeze: false,
      freezeTitle: "",
      freezeMsg: "",
      last_invoice: "",
      logged_out: false,
      // Pay In/Out properties (now for Petty Cash)
      payInDialog: false,
      payOutDialog: false,
      payInAmount: "",
      payInNote: "",
      payOutAmount: "",
      payOutNote: "",
      payInTotal: 0,
      payOutTotal: 0,
      payInEntries: [],
      payOutEntries: [],
      rules: {
        required: (value) => !!value || "Required",
        requiredNote: (value) => !!value || "Note is required",
        positiveNumber: (value) => (value > 0 || "Must be greater than 0"),
      },
    };
  },
  methods: {
    changePage(key) {
      this.$emit("changePage", key);
    },
    go_desk() {
      window.location.href = "/";
    },
    go_about() {
      window.open("https://github.com/yrestom/POS-Awesome", "_blank").focus();
    },
    close_shift_dialog() {
      evntBus.$emit("open_closing_dialog");
    },
    show_mesage(data) {
      this.snack = true;
      this.snackColor = data.color;
      this.snackText = data.text;
    },
    async logOut() {
      try {
        this.freeze = true;
        this.freezeTitle = "Logging out";
        this.freezeMsg = "Please wait...";

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

        if (!response.ok) {
          throw new Error(`Logout failed with status: ${response.status}`);
        }

        this.clearSessionAndRedirect();
      } catch (error) {
        this.show_mesage({
          text: `Logout failed: ${error.message}`,
          color: "error",
        });
        this.freeze = false;
        console.error("Logout error:", error);
      }
    },
    clearSessionAndRedirect() {
      this.logged_out = true;
      localStorage.clear();
      sessionStorage.clear();
      document.cookie.split(";").forEach((c) => {
        document.cookie = c
          .replace(/^ +/, "")
          .replace(/=.*/, `=;expires=${new Date().toUTCString()};path=/`);
      });
      window.location.replace(`/login?nocache=${Date.now()}`);
    },
    print_last_invoice() {
      if (!this.last_invoice) return;
      
      const print_format =
        this.pos_profile.print_format_for_online ||
        this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url = `${frappe.urllib.get_base_url()}/printview?doctype=Sales%20Invoice&name=${
        this.last_invoice
      }&trigger_print=1&format=${print_format}&no_letterhead=${letter_head}`;
      
      const printWindow = window.open(url, "Print");
      printWindow.addEventListener("load", () => printWindow.print(), true);
    },
    async submitPettyCashPayIn() {
      if (!this.validatePayment(this.payInAmount, this.payInNote)) return;

      const amount = parseFloat(this.payInAmount);
      const currentBalance = this.payInTotal - this.payOutTotal;

      try {
        this.freeze = true;
        this.freezeTitle = "Processing Petty Cash Pay In";
        this.freezeMsg = "Please wait...";

        const response = await frappe.call({
          method: "posawesome.posawesome.api.petty_cash.create_petty_cash",
          args: {
            date: frappe.datetime.now_date(),
            entry_type: "Pay In",
            pos_profile: this.pos_profile.name,
            amount: amount,
            note: this.payInNote,
          },
        });

        if (response.message.status === "success") {
          this.show_mesage({
            text: "Petty Cash Pay In created and submitted",
            color: "success",
          });
          this.payInTotal += amount;
          this.payInEntries.push({
            amount,
            note: this.payInNote,
          });
          this.emitPaymentUpdate(amount, 0);
        } else {
          this.show_mesage({
            text: response.message.message || "Failed to process Petty Cash Pay In",
            color: "error",
          });
        }
      } catch (error) {
        this.show_mesage({
          text: `Petty Cash Pay In Error: ${error.message || "Unknown error"}`,
          color: "error",
        });
        console.error("Petty Cash Pay In error:", error);
      } finally {
        this.freeze = false;
        this.resetPaymentForm("payIn");
      }
    },
    async submitPettyCashPayOut() {
      if (!this.validatePayment(this.payOutAmount, this.payOutNote)) return;

      const amount = parseFloat(this.payOutAmount);
      const availableBalance = this.payInTotal - this.payOutTotal;

      if (amount > availableBalance) {
        this.show_mesage({
          text: "Insufficient balance for Pay Out",
          color: "error",
        });
        return;
      }

      try {
        this.freeze = true;
        this.freezeTitle = "Processing Petty Cash Pay Out";
        this.freezeMsg = "Please wait...";

        const response = await frappe.call({
          method: "posawesome.posawesome.api.petty_cash.create_petty_cash",
          args: {
            date: frappe.datetime.now_date(),
            entry_type: "Pay Out",
            pos_profile: this.pos_profile.name,
            amount: amount,
            note: this.payOutNote,
          },
        });

        if (response.message.status === "success") {
          this.show_mesage({
            text: "Petty Cash Pay Out created and submitted",
            color: "success",
          });
          this.payOutTotal += amount;
          this.payOutEntries.push({
            amount,
            note: this.payOutNote,
          });
          this.emitPaymentUpdate(0, amount);
        } else {
          this.show_mesage({
            text: response.message.message || "Failed to process Petty Cash Pay Out",
            color: "error",
          });
        }
      } catch (error) {
        this.show_mesage({
          text: `Petty Cash Pay Out Error: ${error.message || "Unknown error"}`,
          color: "error",
        });
        console.error("Petty Cash Pay Out error:", error);
      } finally {
        this.freeze = false;
        this.resetPaymentForm("payOut");
      }
    },
    validatePayment(amount, note) {
      if (!amount || amount <= 0) {
        this.show_mesage({
          text: "Please enter a valid amount greater than 0",
          color: "error",
        });
        return false;
      }
      if (!note || note.trim() === "") {
        this.show_mesage({
          text: "Please provide a note for the transaction",
          color: "error",
        });
        return false;
      }
      return true;
    },
    emitPaymentUpdate(payInAmount, payOutAmount) {
      evntBus.$emit("update-piti-totals", {
        payInAmount,
        payOutAmount,
        payInEntries: this.payInEntries,
        payOutEntries: this.payOutEntries,
      });
    },
    showSuccessMessage(type, amount) {
      this.show_mesage({
        text: `${type} of $${amount} submitted`,
        color: "success",
      });
    },
    resetPaymentForm(type) {
      if (type === "payIn") {
        this.payInAmount = "";
        this.payInNote = "";
        this.payInDialog = false;
      } else {
        this.payOutAmount = "";
        this.payOutNote = "";
        this.payOutDialog = false;
      }
    },
  },
  created() {
    this.$nextTick(() => {
      evntBus.$on("show_mesage", this.show_mesage);
      evntBus.$on("set_company", (data) => {
        this.company = data.name;
        this.company_img = data.company_logo || this.company_img;
      });
      evntBus.$on("register_pos_profile", (data) => {
        this.pos_profile = data.pos_profile || {};
        if (this.pos_profile.posa_use_pos_awesome_payments && this.items.length !== 2) {
          this.items.push({ text: "Payments", icon: "mdi-cash-register" });
        }
      });
      evntBus.$on("set_last_invoice", (data) => (this.last_invoice = data));
      evntBus.$on("freeze", (data) => {
        this.freeze = true;
        this.freezeTitle = data.title;
        this.freezeMsg = data.msg;
      });
      evntBus.$on("unfreeze", () => {
        this.freeze = false;
        this.freezeTitle = "";
        this.freezeMsg = "";
      });
    });
  },
  beforeDestroy() {
    evntBus.$off("show_mesage");
    evntBus.$off("set_company");
    evntBus.$off("register_pos_profile");
    evntBus.$off("set_last_invoice");
    evntBus.$off("freeze");
    evntBus.$off("unfreeze");
  },
};
</script>

<style scoped>
.margen-top {
  margin-top: 0px;
}

.pay-btn {
  height: 36px !important;
  min-width: 80px !important;
  border-radius: 4px;
  text-transform: uppercase;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.v-app-bar {
  transition: height 0.3s ease;
}

.top-center-snackbar {
  left: 50%;
  transform: translateX(-50%);
  right: auto !important;
}
</style>
