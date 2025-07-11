<template>
  <div>
    <v-card
      class="selection mx-auto grey lighten-5 mt-3"
      style="max-height: 75vh; height: 75vh"
    >
      <v-progress-linear
        :active="loading"
        :indeterminate="loading"
        absolute
        top
        color="info"
      ></v-progress-linear>
      <v-row class="items px-2 py-1">
        <v-col class="pb-0 mb-2">
          <v-text-field
            dense
            clearable
            autofocus
            outlined
            color="primary"
            :label="__('Search Item by (Item Code/Barcode/Name)')"
            hint="Search Item by (Item Code/Barcode/Name)"
            background-color="white"
            hide-details
            v-model="debounce_search"
            @keydown.esc="esc_event"
            @keydown.enter="search_onchange"
            ref="debounce_search"
          ></v-text-field>
        </v-col>
        <v-col cols="3" class="pb-0 mb-2" v-if="pos_profile.posa_input_qty">
          <v-text-field
            dense
            outlined
            color="primary"
            :label="__('Quantity')"
            background-color="white"
            hide-details
            v-model.number="qty"
            type="number"
            @keydown.enter="enter_event"
            @keydown.esc="esc_event"
          ></v-text-field>
        </v-col>
        <v-col cols="2" class="pb-0 mb-2" v-if="pos_profile.posa_new_line">
          <v-checkbox
            v-model="new_line"
            color="accent"
            value="true"
            label="NLine"
            dense
            hide-details
          ></v-checkbox>
        </v-col>
        <v-col cols="12" class="pt-0 mt-0">
          <div fluid class="items" v-if="items_view == 'card'">
            <v-row dense class="overflow-y-auto" style="max-height: 67vh">
              <v-col
                v-for="(item, idx) in filtred_items"
                :key="idx"
                xl="2"
                lg="3"
                md="6"
                sm="6"
                cols="6"
                min-height="50"
              >
                <v-card hover="hover" @click="add_item(item)">
                  <v-img
                    :src="
                      item.image ||
                      '/assets/posawesome/js/posapp/components/pos/placeholder-image.png'
                    "
                    class="white--text align-end"
                    gradient="to bottom, rgba(0,0,0,0), rgba(0,0,0,0.4)"
                    height="100px"
                  >
                    <v-card-text
                      v-text="item.item_name"
                      class="text-caption px-1 pb-0"
                    ></v-card-text>
                  </v-img>
                  <v-card-text class="text--primary pa-1">
                    <div class="text-caption primary--text">
                      {{ currencySymbol(item.currency) || "" }}
                      {{ formatCurrency(item.rate) || 0 }}
                    </div>
                    <div class="text-caption golden--text">
                      {{ item.stock_uom || "" }}
                    </div>
                    <div class="text-caption" v-if="item.actual_qty !== undefined">
                      <span :style="{color: item.actual_qty >= 0 ? '#4CAF50' : '#F44336'}">
                        {{ __('Qty') }}: {{ formatFloat(item.actual_qty) }}
                      </span>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </div>
          <div fluid class="items" v-if="items_view == 'list'">
            <div class="my-0 py-0 overflow-y-auto" style="max-height: 65vh">
              <v-data-table
                :headers="getItemsHeaders()"
                :items="filtred_items"
                item-key="item_code"
                class="elevation-1"
                :items-per-page="itemsPerPage"
                hide-default-footer
                @click:row="add_item_table"
              >
                <template v-slot:item.rate="{ item }">
                  <span class="primary--text">
                    {{ formatCurrency(item.rate) }}
                  </span>
                </template>
                <template v-slot:item.actual_qty="{ item }">
                  {{ formatFloat(item.actual_qty) }}
                </template>
              </v-data-table>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card>
    <v-card class="cards mb-0 mt-3 pa-2 grey lighten-5">
      <v-row no-gutters align="center" justify="center">
        <v-col cols="12">
          <v-select
            :items="items_group"
            :label="__('Item Group')"
            dense
            outlined
            hide-details
            v-model="item_group"
            v-on:change="search_onchange"
          ></v-select>
        </v-col>
        <v-col cols="3" class="mt-1">
          <v-btn-toggle
            v-model="items_view"
            color="primary"
            group
            dense
            rounded
          >
            <v-btn small value="list">{{ __("List") }}</v-btn>
            <v-btn small value="card">{{ __("Images") }}</v-btn>
          </v-btn-toggle>
        </v-col>
        <v-col cols="4" class="mt-2">
          <v-btn small block color="primary" text @click="show_coupons"
            >{{ couponsCount }} {{ __("Coupons") }}</v-btn
          >
        </v-col>
        <v-col cols="5" class="mt-2">
          <v-btn small block color="primary" text @click="show_offers"
            >{{ offersCount }} {{ __("Offers") }} : {{ appliedOffersCount }}
            {{ __("Applied") }}</v-btn
          >
        </v-col>
      </v-row>
    </v-card>
  </div>
</template>

<script>
import { evntBus } from "../../bus";
import format from "../../format";
import _ from "lodash";
export default {
  mixins: [format],
  data: () => ({
    pos_profile: "",
    flags: {},
    items_view: "list",
    item_group: "ALL",
    loading: false,
    items_group: ["ALL"],
    items: [],
    search: "",
    first_search: "",
    itemsPerPage: 1000,
    offersCount: 0,
    appliedOffersCount: 0,
    couponsCount: 0,
    appliedCouponsCount: 0,
    customer_price_list: null,
    customer: null,
    new_line: false,
    qty: 1,
  }),

  watch: {
    filtred_items(new_value, old_value) {
      if (!this.pos_profile.posa_use_limit_search) {
        if (new_value.length != old_value.length) {
          this.update_items_details(new_value);
        }
      }
    },
    customer() {
      this.get_items();
    },
    new_line() {
      evntBus.emit("set_new_line", this.new_line);
    },
  },

  methods: {
    show_offers() {
      evntBus.emit("show_offers", "true");
    },
    show_coupons() {
      evntBus.emit("show_coupons", "true");
    },
    get_items() {
      if (!this.pos_profile) {
        console.error('[ItemsSelector] No POS Profile');
        return;
      }
      const vm = this;
      this.loading = true;
      let search = this.get_search(this.first_search);
      let gr = "";
      let sr = "";
      if (search) {
        sr = search;
      }
      if (vm.item_group != "ALL") {
        gr = vm.item_group.toLowerCase();
      }
      if (
        vm.pos_profile.posa_local_storage &&
        localStorage.items_storage &&
        !vm.pos_profile.posa_use_limit_search
      ) {
        vm.items = JSON.parse(localStorage.getItem("items_storage"));
        evntBus.emit("set_all_items", vm.items);
        vm.loading = false;
        console.info('[ItemsSelector] Loaded items from localStorage');
      }
      frappe.call({
        method: "posawesome.posawesome.api.posapp.get_items",
        args: {
          pos_profile: vm.pos_profile,
          price_list: vm.customer_price_list,
          item_group: gr,
          search_value: sr,
          customer: vm.customer,
        },
        callback: function (r) {
          if (r.message) {
            vm.items = r.message;
            evntBus.emit("set_all_items", vm.items);
            vm.loading = false;
            console.info('[ItemsSelector] Items loaded from API:', r.message.length);
            if (
              vm.pos_profile.posa_local_storage &&
              !vm.pos_profile.posa_use_limit_search
            ) {
              localStorage.setItem("items_storage", "");
              try {
                localStorage.setItem(
                  "items_storage",
                  JSON.stringify(r.message)
                );
                console.info('[ItemsSelector] Items saved to localStorage');
              } catch (e) {
                console.error('[ItemsSelector] Error saving items to localStorage:', e);
              }
            }
            if (vm.pos_profile.posa_use_limit_search) {
              vm.enter_event();
            }
          }
        },
      });
    },
    get_items_groups() {
      if (!this.pos_profile) {
        console.log("No POS Profile");
        return;
      }
      if (this.pos_profile.item_groups.length > 0) {
        this.pos_profile.item_groups.forEach((element) => {
          if (element.item_group !== "All Item Groups") {
            this.items_group.push(element.item_group);
          }
        });
      } else {
        const vm = this;
        frappe.call({
          method: "posawesome.posawesome.api.posapp.get_items_groups",
          args: {},
          callback: function (r) {
            if (r.message) {
              r.message.forEach((element) => {
                vm.items_group.push(element.name);
              });
            }
          },
        });
      }
    },
    getItemsHeaders() {
      const items_headers = [
        {
          title: __("Item Name"),
          align: "start",
          sortable: true,
          key: "item_name",
        },
        {
          title: __("Code"),
          align: "start",
          sortable: true,
          key: "item_code",
        },
        { title: __("Price"), key: "rate", align: "start" },
        { title: __("Available Quantity"), value: "actual_qty", align: "start" },
        { title: __("Unit of Measure"), key: "stock_uom", align: "start" },
      ];
      if (!this.pos_profile.posa_display_item_code) {
        items_headers.splice(1, 1);
      }

      return items_headers;
    },
    add_item_table(event, item){
      item = { ...item.item };
      if (item.has_variants) {
        evntBus.emit("open_variants_model", item, this.items);
      } else {
        if (!item.qty || item.qty === 1) {
          item.qty = Math.abs(this.qty);
        }
        console.info('[ItemsSelector] Adding item:', item);
        evntBus.emit("add_item", item);
        this.qty = 1;
      }
    },
    add_item(item) {
      item = { ...item };
      if (item.has_variants) {
        console.info('[ItemsSelector] Item has variants, opening variants model:', item);
        evntBus.emit("open_variants_model", item, this.items);
      } else {
        if (!item.qty || item.qty === 1) {
          item.qty = Math.abs(this.qty);
        }
        console.info('[ItemsSelector] Adding item:', item);
        evntBus.emit("add_item", item);
        this.qty = 1;
      }
    },
    enter_event() {
      let match = false;
      // Check for matching search items
      if (!this.filtred_items.length || !this.first_search) {
        console.error('[ItemsSelector] No filtered items or no search value');
        return;
      }
      this.get_items();
      const qty = this.get_item_qty(this.first_search);
      const new_item = { ...this.filtred_items[0] };
      new_item.qty = parseFloat(qty) || Math.abs(this.qty);
      if (this.first_search.startsWith(this.pos_profile.posa_scale_barcode_start)) {
        console.info('[ItemsSelector] Scale barcode detected:', this.first_search);
        this.add_item(new_item);
        this.search = null;
        this.first_search = null;
        this.debounce_search = null;
        this.qty = 1;
        this.$refs.debounce_search.focus();
        return;
      }
      else if ( this.first_search && ( this.first_search.startsWith("91") || this.first_search.startsWith("92") || this.first_search.startsWith("93"))) {
        console.info('[ItemsSelector] Special barcode detected (91/92/93):', this.first_search);
        this.add_item(new_item);
        this.search = null;
        this.first_search = null;
        this.debounce_search = null;
        this.qty = 1;
        this.$refs.debounce_search.focus();
        return;
      }
      new_item.item_barcode.forEach((element) => {
        if (this.search == element.barcode) {
          new_item.uom = element.posa_uom;
          match = true;
        }
      });
      if (
        !new_item.to_set_serial_no &&
        new_item.has_serial_no &&
        this.pos_profile.posa_search_serial_no
      ) {
        new_item.serial_no_data.forEach((element) => {
          if (this.search && element.serial_no == this.search) {
            new_item.to_set_serial_no = this.first_search;
            match = true;
          }
        });
      }
      if (this.flags.serial_no) {
        new_item.to_set_serial_no = this.flags.serial_no;
      }
      if (
        !new_item.to_set_batch_no &&
        new_item.has_batch_no &&
        this.pos_profile.posa_search_batch_no
      ) {
        new_item.batch_no_data.forEach((element) => {
          if (this.search && element.batch_no == this.search) {
            new_item.to_set_batch_no = this.first_search;
            new_item.batch_no = this.first_search;
            match = true;
          }
        });
      }
      if (this.flags.batch_no) {
        new_item.to_set_batch_no = this.flags.batch_no;
      }
      if (match) {
        console.info('[ItemsSelector] Barcode/serial/batch match found, adding item:', new_item);
        this.add_item(new_item);
        this.search = null;
        this.first_search = null;
        this.debounce_search = null;
        this.flags.serial_no = null;
        this.flags.batch_no = null;
        this.qty = 1;
        this.$refs.debounce_search.focus();
      }
    },
    search_onchange() {
      const vm = this;
      if (vm.pos_profile.posa_use_limit_search) {
        vm.get_items();
      } else {
        vm.enter_event();
      }
    },
    get_item_qty(first_search) {
      let scal_qty = Math.abs(this.qty);

      if (first_search && first_search.startsWith(this.pos_profile.posa_scale_barcode_start)) {
        let pesokg1 = first_search.substring(7, 12);
        let weight = parseInt(pesokg1, 10);
        scal_qty = weight / 1000;
      }
      else if (first_search && (first_search.startsWith("91") || first_search.startsWith("92") || first_search.startsWith("93"))) {
        scal_qty = 1;
      }

      return scal_qty;
    },

    get_search(first_search) {
      let search_term = "";
      if (
        first_search &&
        first_search.startsWith(this.pos_profile.posa_scale_barcode_start)
      ) {
        search_term = first_search.substr(2, 5);
      } else {
        search_term = first_search;
      }
      return search_term;
    },
    esc_event() {
      this.search = null;
      this.first_search = null;
      this.qty = 1;
      this.$refs.debounce_search.focus();
    },
    update_items_details(items) {
      const vm = this;
      frappe.call({
        method: "posawesome.posawesome.api.posapp.get_items_details",
        args: {
          pos_profile: vm.pos_profile,
          items_data: items,
        },
        callback: function (r) {
          if (r.message) {
            items.forEach((item) => {
              const updated_item = r.message.find(
                (element) => element.item_code == item.item_code
              );
              item.actual_qty = updated_item.actual_qty;
              item.serial_no_data = updated_item.serial_no_data;
              item.batch_no_data = updated_item.batch_no_data;
              item.item_uoms = updated_item.item_uoms;
            });
          }
        },
      });
    },
    update_cur_items_details() {
      this.update_items_details(this.filtred_items);
    },
    scan_barcode() {
      const vm = this;
      onScan.attachTo(document, {
        suffixKeyCodes: [],
        keyCodeMapper: function (oEvent) {
          oEvent.stopImmediatePropagation();
          return onScan.decodeKeyEvent(oEvent);
        },
        onScan: function (sCode) {
          setTimeout(() => {
            vm.trigger_onscan(sCode);
          }, 300);
        },
      });
    },
    trigger_onscan(sCode) {
      // Set the scanned barcode as the initial search value
      this.first_search = sCode;
      this.search = sCode;
      // Process scale barcode (starts with prefix "44")
      if (sCode.startsWith(this.pos_profile.posa_scale_barcode_start)) {
        const weight = this.get_item_qty(sCode);
        this.qty = parseFloat(weight) || 1;
        if (this.filtred_items.length > 0) {
          const new_item = { ...this.filtred_items[0] };
          new_item.qty = this.qty;
          this.add_item(new_item);
          console.info('[ItemsSelector] Barcode scan (scale):', sCode, 'Weight:', this.qty, 'First Item:', this.filtred_items[0]);
          frappe.utils.play_sound("error");
          this.search = null;
          this.first_search = null;
          this.debounce_search = null;
          this.qty = 1;
          this.$nextTick(() => {
            this.$refs.debounce_search.focus();
          });
        }
      }
      // --- Processing barcodes starting with 91, 92, or 93 ---
      // For these barcodes, extract the 5-digit item code and directly add the item
      else if (sCode.startsWith("91") || sCode.startsWith("92") || sCode.startsWith("93")) {
        const item_code = sCode.substring(2, 7);
        console.info('[ItemsSelector] Barcode scan (91/92/93):', sCode, 'Extracted Item Code:', item_code);
        const found_item = this.items.find((item) => item.item_code == item_code);
        if (found_item) {
          const new_item = { ...found_item };
          new_item.qty = 1;
          this.add_item(new_item);
          console.info('[ItemsSelector] Added item without API calls:', new_item);
        } else {
          console.error('[ItemsSelector] Item not found for code:', item_code);
        }
        // Reset search fields and focus search input
        this.search = null;
        this.first_search = null;
        this.debounce_search = null;
        this.qty = 1;
        this.$refs.debounce_search.focus();
        return;
      }
      // --- End of processing for 91/92/93 ---
      else {
        // For regular barcodes, get the quantity and process via enter_event()
        const weight = this.get_item_qty(sCode);
        this.qty = parseFloat(weight) || 1;
        this.enter_event();
      }
    },
    generateWordCombinations(inputString) {
      const words = inputString.split(" ");
      const combinations = [];
      function permute(arr, m = []) {
        if (arr.length === 0) {
          combinations.push(m.join(" "));
        } else {
          for (let i = 0; i < arr.length; i++) {
            const current = arr.slice();
            const next = current.splice(i, 1);
            permute(current.slice(), m.concat(next));
          }
        }
      }
      permute(words);
      return combinations;
    },
  },
  computed: {
    filtred_items() {
      this.search = this.get_search(this.first_search);
      if (!this.pos_profile.posa_use_limit_search) {
        let filtred_list = [];
        let filtred_group_list = [];
        if (this.item_group != "ALL") {
          filtred_group_list = this.items.filter((item) =>
            item.item_group.toLowerCase().includes(this.item_group.toLowerCase())
          );
        } else {
          filtred_group_list = this.items;
        }
        if (!this.search || this.search.length < 3) {
          if (
            this.pos_profile.posa_show_template_items &&
            this.pos_profile.posa_hide_variants_items
          ) {
            return (filtred_list = filtred_group_list
              .filter((item) => !item.variant_of)
              .slice(0, 50));
          } else {
            return (filtred_list = filtred_group_list.slice(0, 50));
          }
        } else if (this.search) {
          filtred_list = filtred_group_list.filter((item) => {
            let found = false;
            for (let element of item.item_barcode) {
              if (element.barcode == this.search) {
                found = true;
                break;
              }
            }
            return found;
          });
          if (filtred_list.length == 0) {
            filtred_list = filtred_group_list.filter((item) =>
              item.item_code.toLowerCase().includes(this.search.toLowerCase())
            );
            if (filtred_list.length == 0) {
              const search_combinations = this.generateWordCombinations(this.search);
              filtred_list = filtred_group_list.filter((item) => {
                let found = false;
                for (let element of search_combinations) {
                  element = element.toLowerCase().trim();
                  let element_regex = new RegExp(`.*${element.split("").join(".*")}.*`);
                  if (element_regex.test(item.item_name.toLowerCase())) {
                    found = true;
                    break;
                  }
                }
                return found;
              });
            }
            if (
              filtred_list.length == 0 &&
              this.pos_profile.posa_search_serial_no
            ) {
              filtred_list = filtred_group_list.filter((item) => {
                let found = false;
                for (let element of item.serial_no_data) {
                  if (element.serial_no == this.search) {
                    found = true;
                    this.flags.serial_no = null;
                    this.flags.serial_no = this.search;
                    break;
                  }
                }
                return found;
              });
            }
            if (
              filtred_list.length == 0 &&
              this.pos_profile.posa_search_batch_no
            ) {
              filtred_list = filtred_group_list.filter((item) => {
                let found = false;
                for (let element of item.batch_no_data) {
                  if (element.batch_no == this.search) {
                    found = true;
                    this.flags.batch_no = null;
                    this.flags.batch_no = this.search;
                    break;
                  }
                }
                return found;
              });
            }
          }
        }
        if (
          this.pos_profile.posa_show_template_items &&
          this.pos_profile.posa_hide_variants_items
        ) {
          return filtred_list.filter((item) => !item.variant_of).slice(0, 50);
        } else {
          return filtred_list.slice(0, 50);
        }
      } else {
        return this.items.slice(0, 50);
      }
    },
    debounce_search: {
      get() {
        return this.first_search;
      },
      set: _.debounce(function (newValue) {
        this.first_search = newValue;
        // alaa edit for enter_event
        // this.enter_event();
      }, 300),
    },
  },
  created: function () {
    this.$nextTick(function () {});
    evntBus.on("register_pos_profile", (data) => {
      this.pos_profile = data.pos_profile;
      this.get_items();
      this.get_items_groups();
      this.items_view = this.pos_profile.posa_default_card_view ? "card" : "list";
    });
    evntBus.on("update_cur_items_details", () => {
      this.update_cur_items_details();
    });
    evntBus.on("update_offers_counters", (data) => {
      this.offersCount = data.offersCount;
      this.appliedOffersCount = data.appliedOffersCount;
    });
    evntBus.on("update_coupons_counters", (data) => {
      this.couponsCount = data.couponsCount;
      this.appliedCouponsCount = data.appliedCouponsCount;
    });
    evntBus.on("update_customer_price_list", (data) => {
      this.customer_price_list = data;
    });
    evntBus.on("update_customer", (data) => {
      this.customer = data;
    });
  },
  mounted() {
    this.scan_barcode();
  },
};
</script>

<style scoped></style>
