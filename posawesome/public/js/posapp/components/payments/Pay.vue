<template>
  <div fluid>
    <v-row v-show="!dialog">
      <v-col md="8" cols="12" class="pb-2 pr-0">
        <v-card
          class="main mx-auto grey lighten-5 mt-3 p-3 pb-16 overflow-y-auto"
          style="max-height: 94vh; height: 94vh"
        >
          <Customer></Customer>
          <v-divider></v-divider>
          <div>
            <v-row>
              <v-col md="7" cols="12">
                <p>
                  <strong>{{ __("Invoices") }}</strong>
                  <span v-if="total_outstanding_amount" class="primary--text"
                    >{{ __("Total Outstanding Amounts") }} :
                    {{ currencySymbol(pos_profile.currency) }}
                    {{ formatCurrency(total_outstanding_amount) }}</span
                  >
                </p>
              </v-col>
              <v-col md="5" cols="12">
                <p v-if="total_selected_invoices" class="golden--text text-end">
                  <span>{{ __("Total Selected :") }}</span>
                  <span>
                    {{ currencySymbol(pos_profile.currency) }}
                    {{ formatCurrency(total_selected_invoices) }}
                  </span>
                </p>
              </v-col>
            </v-row>
            <v-row align="center" no-gutters class="mb-1">
              <v-col md="4" cols="12">
                <v-select
                  dense
                  outlined
                  hide-details
                  clearable
                  background-color="white"
                  v-model="pos_profile_search"
                  :items="pos_profiles_list"
                  item-value="name"
                  label="Select Shift"
                ></v-select>
              </v-col>
              <v-col> </v-col>
              <v-col md="3" cols="12">
                <v-btn
                  block
                  color="warning"
                  dark
                  @click="get_outstanding_invoices"
                  >{{ __("Search") }}</v-btn
                >
              </v-col>
            </v-row>
            <v-data-table
              :headers="invoices_headers"
              :items="outstanding_invoices"
              item-key="name"
              class="elevation-1 mt-0"
              show-select
              v-model="selected_invoices"
              :loading="invoices_loading"
              checkbox-color="primary"
              @item-selected="onInvoiceSelected"
            >
              <template v-slot:item.grand_total="{ item }">
                {{ currencySymbol(item.currency) }}
                {{ formatCurrency(item.grand_total) }}
              </template>
              <template v-slot:item.outstanding_amount="{ item }">
                <span class="primary--text"
                  >{{ currencySymbol(item.currency) }}
                  {{ formatCurrency(item.outstanding_amount) }}</span
                >
              </template>
            </v-data-table>
            <v-divider></v-divider>
          </div>
          <div
            v-if="
              pos_profile.posa_allow_reconcile_payments &&
              unallocated_payments.length
            "
          >
            <v-row>
              <v-col md="7" cols="12">
                <p>
                  <strong>{{ __("Payments") }}</strong>
                  <span v-if="total_unallocated_amount" class="primary--text">
                    {{ __("Unallocated Payments") }} :
                    {{ currencySymbol(pos_profile.currency) }}
                    {{ formatCurrency(total_unallocated_amount) }}
                  </span>
                </p>
              </v-col>
              <v-col md="5" cols="12">
                <p v-if="total_selected_payments" class="golden--text text-end">
                  <span>{{ __("Total Selected :") }}</span>
                  <span>
                    {{ currencySymbol(pos_profile.currency) }}
                    {{ formatCurrency(total_selected_payments) }}
                  </span>
                </p>
              </v-col>
            </v-row>
            <v-data-table
              :headers="unallocated_payments_headers"
              :items="unallocated_payments"
              item-key="name"
              class="elevation-1 mt-0"
              :single-select="singleSelect"
              show-select
              v-model="selected_payments"
              :loading="unallocated_payments_loading"
              checkbox-color="primary"
            >
              <template v-slot:item.paid_amount="{ item }">
                {{ currencySymbol(item.currency) }}
                {{ formatCurrency(item.paid_amount) }}
              </template>
              <template v-slot:item.unallocated_amount="{ item }">
                <span class="primary--text"
                  >{{ currencySymbol(item.currency) }}
                  {{ formatCurrency(item.unallocated_amount) }}</span
                >
              </template>
            </v-data-table>
            <v-divider></v-divider>
          </div>
          <div v-if="pos_profile.posa_allow_mpesa_reconcile_payments">
            <v-row>
              <v-col md="8" cols="12">
                <p>
                  <span
                    ><strong>{{ __("Search for Mobile Payments") }}</strong></span
                  >
                </p>
              </v-col>
              <v-col md="4" cols="12" v-if="total_selected_mpesa_payments">
                <p class="golden--text text-end">
                  <span>{{ __("Total Selected :") }}</span>
                  <span>
                    {{ currencySymbol(pos_profile.currency) }}
                    {{ formatCurrency(total_selected_mpesa_payments) }}
                  </span>
                </p>
              </v-col>
            </v-row>
            <v-row align="center" no-gutters class="mb-1">
              <v-col md="4" cols="12" class="mr-1">
                <v-text-field
                  dense
                  outlined
                  color="primary"
                  :label="__('Search by customer name')"
                  background-color="white"
                  hide-details
                  v-model="mpesa_search_name"
                  clearable
                ></v-text-field>
              </v-col>
              <v-col md="4" cols="12" class="mr-1">
                <v-text-field
                  dense
                  outlined
                  color="primary"
                  :label="__('Search by phone number')"
                  background-color="white"
                  hide-details
                  v-model="mpesa_search_mobile"
                  clearable
                ></v-text-field>
              </v-col>
              <v-col> </v-col>
              <v-col md="3" cols="12">
                <v-btn
                  block
                  color="warning"
                  dark
                  @click="get_draft_mpesa_payments_register"
                  >{{ __("Search") }}</v-btn
                >
              </v-col>
            </v-row>
            <v-data-table
              :headers="mpesa_payment_headers"
              :items="mpesa_payments"
              item-key="name"
              class="elevation-1 mt-0"
              :single-select="singleSelect"
              show-select
              v-model="selected_mpesa_payments"
              :loading="mpesa_payments_loading"
              checkbox-color="primary"
            >
              <template v-slot:item.amount="{ item }">
                <span class="primary--text">
                  {{ currencySymbol(item.currency) }}
                  {{ formatCurrency(item.amount) }}
                </span>
              </template>
            </v-data-table>
          </div>
        </v-card>
      </v-col>
      <v-col md="4" cols="12" class="pb-3">
        <v-card
          class="invoices mx-auto grey lighten-5 mt-3 p-3"
          style="max-height: 94vh; height: 94vh"
        >
          <strong>
            <h4 class="primary--text">Totals</h4>
            <v-row>
              <v-col md="7" class="mt-1">
                <span>{{ __("Invoices Total:") }}</span>
              </v-col>
              <v-col md="5">
                <v-text-field
                  class="p-0 m-0"
                  dense
                  color="primary"
                  background-color="white"
                  hide-details
                  :value="formatCurrency(total_selected_invoices)"
                  total_selected_invoices
                  readonly
                  flat
                  :prefix="currencySymbol(pos_profile.currency)"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-row v-if="total_selected_payments">
              <v-col md="7" class="mt-1"
                ><span>{{ __("Payments Total:") }}</span></v-col
              >
              <v-col md="5">
                <v-text-field
                  class="p-0 m-0"
                  dense
                  color="primary"
                  background-color="white"
                  hide-details
                  :value="formatCurrency(total_selected_payments)"
                  total_selected_payments
                  readonly
                  flat
                  :prefix="currencySymbol(pos_profile.currency)"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-row v-if="total_selected_mpesa_payments">
              <v-col md="7" class="mt-1"
                ><span>{{ __("MPESA Total:") }}</span></v-col
              >
              <v-col md="5">
                <v-text-field
                  class="p-0 m-0"
                  dense
                  color="primary"
                  background-color="white"
                  hide-details
                  :value="formatCurrency(total_selected_mpesa_payments)"
                  total_selected_mpesa_payments
                  readonly
                  flat
                  :prefix="currencySymbol(pos_profile.currency)"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-divider v-if="payment_methods.length"></v-divider>
            <div v-if="pos_profile.posa_allow_make_new_payments">
              <h4 class="primary--text">Make New Payment</h4>
              <v-row
                v-if="payment_methods.length"
                v-for="method in payment_methods"
                :key="method.row_id"
              >
                <v-col md="7"
                  ><span class="mt-1">{{ __(method.mode_of_payment) }}:</span>
                </v-col>
                <v-col md="5"
                  ><v-text-field
                    class="p-0 m-0"
                    dense
                    color="primary"
                    background-color="white"
                    hide-details
                    :value="formatCurrency(method.amount)"
                    @change="
                      setFormatedCurrency(method, 'amount', null, true, $event)
                    "
                    payments_methods
                    flat
                    :prefix="currencySymbol(pos_profile.currency)"
                  ></v-text-field
                ></v-col>
              </v-row>
            </div>

            <v-divider></v-divider>
            <v-row>
              <v-col md="7">
                <h4 class="primary--text mt-1">{{ __("Difference:") }}</h4>
              </v-col>
              <v-col md="5">
                <v-text-field
                  class="p-0 m-0"
                  dense
                  color="primary"
                  background-color="white"
                  hide-details
                  :value="formatCurrency(total_of_diff)"
                  total_of_diff
                  flat
                  readonly
                  :prefix="currencySymbol(pos_profile.currency)"
                ></v-text-field>
              </v-col>
            </v-row>
          </strong>
          <div
            class="pb-6 pr-6"
            style="position: absolute; bottom: 0; width: 100%"
          >
            <v-btn block color="primary" dark @click="submit">
              {{ __("Submit") }}
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { evntBus } from "../../bus";
import format from "../../format";
import Customer from "../pos/Customer.vue";
import UpdateCustomer from "../pos/UpdateCustomer.vue";

export default {
  mixins: [format],
  data: function () {
    return {
      dialog: false,
      pos_profile: "",
      pos_opening_shift: "",
      customer_name: "",
      customer_info: "",
      company: "",
      singleSelect: false,
      invoices_loading: false,
      unallocated_payments_loading: false,
      mpesa_payments_loading: false,
      payment_methods: [],
      outstanding_invoices: [],
      unallocated_payments: [],
      mpesa_payments: [],
      selected_invoices: [],
      selected_payments: [],
      selected_mpesa_payments: [],
      pos_profiles_list: [],
      pos_profile_search: "",
      payment_methods_list: [],
      mpesa_searchname: "",
      mpesa_search_mobile: "",
      invoices_headers: [
        {
          text: __("Invoice"),
          align: "start",
          sortable: true,
          value: "name",
        },
        {
          text: __("Customer"),
          align: "start",
          sortable: true,
          value: "customer_name",
        },
        {
          text: __("Date"),
          align: "start",
          sortable: true,
          value: "posting_date",
        },
        {
          text: __("Due Date"),
          align: "start",
          sortable: true,
          value: "due_date",
        },
        {
          text: __("Total"),
          align: "end",
          sortable: true,
          value: "grand_total",
        },
        {
          text: __("Outstanding"),
          align: "end",
          sortable: true,
          value: "outstanding_amount",
        },
      ],
      unallocated_payments_headers: [
        {
          text: __("Reference No"),
          align: "start",
          sortable: true,
          value: "name",
        },
        {
          text: __("Customer"),
          align: "start",
          sortable: true,
          value: "customer_name",
        },
        {
          text: __("Date"),
          align: "start",
          sortable: true,
          value: "posting_date",
        },
        {
          text: __("Mode of Payment"),
          align: "start",
          sortable: true,
          value: "mode_of_payment",
        },
        {
          text: __("Paid"),
          align: "end",
          sortable: true,
          value: "paid_amount",
        },
        {
          text: __("Unallocated"),
          align: "end",
          sortable: true,
          value: "unallocated_amount",
        },
      ],
      mpesa_payment_headers: [
        {
          text: __("Payment Number"),
          align: "start",
          sortable: true,
          value: "transid",
        },
        {
          text: __("Full Name"),
          align: "start",
          sortable: true,
          value: "full_name",
        },
        {
          text: __("Phone Number"),
          align: "start",
          sortable: true,
          value: "mobile_no",
        },
        {
          text: __("Date"),
          align: "start",
          sortable: true,
          value: "posting_date",
        },
        {
          text: __("Amount"),
          align: "end",
          sortable: true,
          value: "amount",
        },
      ],
    };
  },

  components: {
    Customer,
    UpdateCustomer,
  },

  methods: {
    check_opening_entry() {
      try {
        console.info('[Pay] check_opening_entry called');
        return frappe
          .call("posawesome.posawesome.api.posapp.check_opening_shift", {
            user: frappe.session.user,
          })
          .then((r) => {
            if (r.message) {
              this.pos_profile = r.message.pos_profile;
              this.pos_opening_shift = r.message.pos_opening_shift;
              this.company = r.message.company.name;
              console.info('[Pay] set pos_profile, pos_opening_shift, company', this.company);
              evntBus.emit("payments_register_pos_profile", r.message);
              evntBus.emit("set_company", r.message.company);
              this.set_payment_methods();
              this.pos_profile_search = r.message.pos_profile.name;
              this.pos_profiles_list.push(this.pos_profile_search);
              this.payment_methods_list = [];
              this.pos_profile.payments.forEach((element) => {
                this.payment_methods_list.push(element.mode_of_payment);
              });
              this.get_available_pos_profiles();
              this.get_outstanding_invoices();
              this.get_draft_mpesa_payments_register();
            } else {
              this.create_opening_voucher();
            }
          });
      } catch (error) {
        console.error('[Pay] Error in check_opening_entry:', error);
      }
    },
    get_available_pos_profiles() {
      try {
        console.info('[Pay] get_available_pos_profiles called');
        if (!this.pos_profile.posa_allow_mpesa_reconcile_payments) return;
        return frappe
          .call(
            "posawesome.posawesome.api.payment_entry.get_available_pos_profiles",
            {
              company: this.company,
              currency: this.pos_profile.currency,
            }
          )
          .then((r) => {
            if (r.message) {
              this.pos_profiles_list = r.message;
            }
          });
      } catch (error) {
        console.error('[Pay] Error in get_available_pos_profiles:', error);
      }
    },
    create_opening_voucher() {
      try {
        console.info('[Pay] create_opening_voucher called');
        this.dialog = true;
      } catch (error) {
        console.error('[Pay] Error in create_opening_voucher:', error);
      }
    },
    fetch_customer_details() {
      try {
        console.info('[Pay] fetch_customer_details called', this.customer_name);
        const vm = this;
        if (this.customer_name) {
          frappe.call({
            method: "posawesome.posawesome.api.posapp.get_customer_info",
            args: {
              customer: vm.customer_name,
            },
            async: false,
            callback: (r) => {
              const message = r.message;
              if (!r.exc) {
                vm.customer_info = {
                  ...message,
                };
                vm.set_mpesa_search_params();
                evntBus.emit("set_customer_info_to_edit", vm.customer_info);
              }
            },
            error: (err) => {
              console.error('[Pay] Error in fetch_customer_details:', err);
            }
          });
        }
      } catch (error) {
        console.error('[Pay] Error in fetch_customer_details:', error);
      }
    },
    onInvoiceSelected(event) {
      try {
        console.info('[Pay] onInvoiceSelected called', event);
        evntBus.emit("set_customer", event.item.customer);
      } catch (error) {
        console.error('[Pay] Error in onInvoiceSelected:', error);
      }
    },
    get_outstanding_invoices() {
      try {
        console.info('[Pay] get_outstanding_invoices called', { customer: this.customer_name, company: this.company });
        this.invoices_loading = true;
        return frappe
          .call(
            "posawesome.posawesome.api.payment_entry.get_outstanding_invoices",
            {
              customer: this.customer_name,
              company: this.company,
              currency: this.pos_profile.currency,
              pos_profile_name: this.pos_profile_search,
            }
          )
          .then((r) => {
            if (r.message) {
              this.outstanding_invoices = r.message;
              this.invoices_loading = false;
            }
          });
      } catch (error) {
        console.error('[Pay] Error in get_outstanding_invoices:', error);
      }
    },
    get_unallocated_payments() {
      try {
        console.info('[Pay] get_unallocated_payments called');
        if (!this.pos_profile.posa_allow_reconcile_payments) return;
        this.unallocated_payments_loading = true;
        if (!this.customer_name) {
          this.unallocated_payments = [];
          this.unallocated_payments_loading = false;
          return;
        }
        return frappe
          .call(
            "posawesome.posawesome.api.payment_entry.get_unallocated_payments",
            {
              customer: this.customer_name,
              company: this.company,
              currency: this.pos_profile.currency,
            }
          )
          .then((r) => {
            if (r.message) {
              this.unallocated_payments = r.message;
              this.unallocated_payments_loading = false;
            }
          });
      } catch (error) {
        console.error('[Pay] Error in get_unallocated_payments:', error);
      }
    },
    set_mpesa_search_params() {
      try {
        console.info('[Pay] set_mpesa_search_params called');
        if (!this.pos_profile.posa_allow_mpesa_reconcile_payments) return;
        if (!this.customer_name) return;
        this.mpesa_search_name = this.customer_info.customer_name.split(" ")[0];
        if (this.customer_info.mobile_no) {
          this.mpesa_search_mobile =
            this.customer_info.mobile_no.substring(0, 4) +
            " ***** " +
            this.customer_info.mobile_no.substring(9);
        }
      } catch (error) {
        console.error('[Pay] Error in set_mpesa_search_params:', error);
      }
    },
    get_draft_mpesa_payments_register() {
      try {
        console.info('[Pay] get_draft_mpesa_payments_register called');
        if (!this.pos_profile.posa_allow_mpesa_reconcile_payments) return;
        const vm = this;
        this.mpesa_payments_loading = true;
        return frappe
          .call("posawesome.posawesome.api.m_pesa.get_mpesa_draft_payments", {
            company: vm.company,
            mode_of_payment: null,
            full_name: vm.mpesa_search_name || null,
            mobile_no: vm.mpesa_search_mobile || null,
            payment_methods_list: vm.payment_methods_list,
          })
          .then((r) => {
            if (r.message) {
              vm.mpesa_payments = r.message;
            } else {
              vm.mpesa_payments = [];
            }
            vm.mpesa_payments_loading = false;
          });
      } catch (error) {
        console.error('[Pay] Error in get_draft_mpesa_payments_register:', error);
      }
    },
    set_payment_methods() {
      try {
        console.info('[Pay] set_payment_methods called');
        if (!this.pos_profile.posa_allow_make_new_payments) return;
        this.payment_methods = [];
        this.pos_profile.payments.forEach((method) => {
          this.payment_methods.push({
            mode_of_payment: method.mode_of_payment,
            amount: 0,
            row_id: method.name,
          });
        });
      } catch (error) {
        console.error('[Pay] Error in set_payment_methods:', error);
      }
    },
    clear_all(with_customer_info = true) {
      try {
        console.info('[Pay] clear_all called', { with_customer_info });
        this.customer_name = "";
        if (with_customer_info) {
          this.customer_info = "";
        }
        this.mpesa_search_mobile = "";
        this.mpesa_search_name = "";
        this.mpesa_payments = [];
        this.selected_mpesa_payments = [];
        this.outstanding_invoices = [];
        this.unallocated_payments = [];
        this.selected_invoices = [];
        this.selected_payments = [];
        this.selected_mpesa_payments = [];
        this.set_payment_methods();
      } catch (error) {
        console.error('[Pay] Error in clear_all:', error);
      }
    },
    submit() {
      try {
        console.info('[Pay] submit called');
        const customer = this.customer_name;
        const vm = this;
        if (!customer) {
          console.error('[Pay] No customer selected');
          frappe.throw(__("Please select a customer"));
          return;
        }
        if (
          this.total_selected_payments == 0 &&
          this.total_selected_mpesa_payments == 0 &&
          this.total_payment_methods == 0
        ) {
          console.error('[Pay] No payment selected');
          frappe.throw(__("Please make a payment or select a payment"));
          return;
        }
        if (
          this.total_selected_payments > 0 &&
          this.selected_invoices.length == 0
        ) {
          console.error('[Pay] No invoice selected for selected payments');
          frappe.throw(__("Please select an invoice"));
          return;
        }
        this.payment_methods.forEach((payment) => {
          payment.amount = flt(payment.amount);
        });
        const payload = {};
        payload.customer = customer;
        payload.company = this.company;
        payload.currency = this.pos_profile.currency;
        payload.pos_opening_shift_name = this.pos_opening_shift.name;
        payload.pos_profile_name = this.pos_profile.name;
        payload.pos_profile = this.pos_profile;
        payload.payment_methods = this.payment_methods;
        payload.selected_invoices = this.selected_invoices;
        payload.selected_payments = this.selected_payments;
        payload.total_selected_invoices = flt(this.total_selected_invoices);
        payload.selected_mpesa_payments = this.selected_mpesa_payments;
        payload.total_selected_payments = flt(this.total_selected_payments);
        payload.total_payment_methods = flt(this.total_payment_methods);
        payload.total_selected_mpesa_payments = flt(
          this.total_selected_mpesa_payments
        );
        frappe.call({
          method: "posawesome.posawesome.api.payment_entry.process_pos_payment",
          args: { payload },
          freeze: true,
          freeze_message: __("Processing payment"),
          callback: function (r) {
            if (r.message) {
              console.info('[Pay] Payment processed successfully', r.message);
              frappe.utils.play_sound("submit");
              vm.clear_all(false);
              vm.customer_name = customer;
              vm.get_outstanding_invoices();
              vm.get_unallocated_payments();
              vm.set_mpesa_search_params();
              vm.get_draft_mpesa_payments_register();
            }
          },
          error: function (err) {
            console.error('[Pay] Error in process_pos_payment:', err);
          }
        });
      } catch (error) {
        console.error('[Pay] Error in submit:', error);
      }
    },
  },

  computed: {
    total_outstanding_amount() {
      return this.outstanding_invoices.reduce(
        (acc, cur) => acc + flt(cur.outstanding_amount),
        0
      );
    },
    total_unallocated_amount() {
      return this.unallocated_payments.reduce(
        (acc, cur) => acc + flt(cur.unallocated_amount),
        0
      );
    },
    total_selected_invoices() {
      return this.selected_invoices.reduce(
        (acc, cur) => acc + flt(cur.outstanding_amount),
        0
      );
    },
    total_selected_payments() {
      return this.selected_payments.reduce(
        (acc, cur) => acc + flt(cur.unallocated_amount),
        0
      );
    },
    total_selected_mpesa_payments() {
      return this.selected_mpesa_payments.reduce(
        (acc, cur) => acc + flt(cur.amount),
        0
      );
    },
    total_payment_methods() {
      return this.payment_methods.reduce(
        (acc, cur) => acc + flt(cur.amount),
        0
      );
    },
    total_of_diff() {
      return flt(
        this.total_selected_invoices -
          this.total_selected_payments -
          this.total_selected_mpesa_payments -
          this.total_payment_methods
      );
    },
  },

  mounted: function () {
    this.$nextTick(function () {
      this.check_opening_entry();
      evntBus.on("update_customer", (customer_name) => {
        this.clear_all(true);
        this.customer_name = customer_name;
        this.fetch_customer_details();
        this.get_outstanding_invoices();
        this.get_unallocated_payments();
        this.get_draft_mpesa_payments_register();
      });
      evntBus.on("fetch_customer_details", () => {
        this.fetch_customer_details();
      });
    });
  },
  beforeDestroy() {
    // Properly clean up event listeners
    evntBus.$off("update_customer");
    evntBus.$off("fetch_customer_details");
  },
};
</script>

<style>
input[total_of_diff] {
  text-align: right;
}
input[payments_methods] {
  text-align: right;
}
input[total_selected_payments] {
  text-align: right;
}
input[total_selected_invoices] {
  text-align: right;
}
input[total_selected_mpesa_payments] {
  text-align: right;
}
</style>
