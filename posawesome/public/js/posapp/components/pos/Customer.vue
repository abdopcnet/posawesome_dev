<template>
  <div>
    <v-autocomplete
      density="compact"
      variant="outlined"
      color="primary"
      :label="__('Customer')"
      v-model="customer"
      :items="customers"
      item-title="customer_name"
      item-value="name"
      :filter="customFilter"
      :disabled="readonly"
      append-icon="mdi-plus"
      @click:append="new_customer"
      prepend-inner-icon="mdi-account-edit"
      @click:prepend-inner="edit_customer"
    >
      <template v-slot:item="{ props, item }">
          <v-list-item
            v-bind="props"
            >
            <v-list-item-title
              class="primary--text subtitle-1"
              v-html="item.customer_name"
            ></v-list-item-title>
            <v-list-item-subtitle
              v-if="item.customer_name != item.name"
              v-html="`ID: ${item.name}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="item.tax_id"
              v-html="`TAX ID: ${item.tax_id}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="item.email_id"
              v-html="`Email: ${item.email_id}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="item.mobile_no"
              v-html="`Mobile No: ${item.mobile_no}`"
            ></v-list-item-subtitle>
            <v-list-item-subtitle
              v-if="item.primary_address"
              v-html="`Primary Address: ${item.primary_address}`"
            ></v-list-item-subtitle>
          </v-list-item>
      </template>
    </v-autocomplete>
    <div class="mb-8">
      <UpdateCustomer></UpdateCustomer>
    </div>
  </div>
</template>

<script>
import { evntBus } from '../../bus';
import UpdateCustomer from './UpdateCustomer.vue';
export default {
  data: () => ({
    pos_profile: '',
    customers: [],
    customer: '',
    readonly: false,
    customer_info: {},
  }),

  components: {
    UpdateCustomer,
  },

  methods: {
    get_customer_names() {
      const vm = this;
      try {
        console.info('[Customer] get_customer_names called');
        if (this.customers.length > 0) {
          return;
        }
        if (vm.pos_profile.posa_local_storage && localStorage.customer_storage) {
          vm.customers = JSON.parse(localStorage.getItem('customer_storage'));
        }
        frappe.call({
          method: 'posawesome.posawesome.api.posapp.get_customer_names',
          args: {
            pos_profile: this.pos_profile.pos_profile,
          },
          callback: function (r) {
            if (r.message) {
              vm.customers = r.message;
              console.info('[Customer] loadCustomers', r.message);
              if (vm.pos_profile.posa_local_storage) {
                localStorage.setItem('customer_storage', '');
                localStorage.setItem(
                  'customer_storage',
                  JSON.stringify(r.message)
                );
              }
            }
          },
          error: function (err) {
            console.error('[Customer] Error in get_customer_names:', err);
          }
        });
      } catch (error) {
        console.error('[Customer] Error in get_customer_names:', error);
      }
    },
    new_customer() {
      try {
        console.info('[Customer] new_customer called');
        evntBus.emit('open_update_customer', null);
      } catch (error) {
        console.error('[Customer] Error in new_customer:', error);
      }
    },
    edit_customer() {
      try {
        console.info('[Customer] edit_customer called', this.customer_info);
        evntBus.emit('open_update_customer', this.customer_info);
      } catch (error) {
        console.error('[Customer] Error in edit_customer:', error);
      }
    },
    customFilter(item, queryText, itemText) {
      try {
        // custom filter for customer search
        const textOne = item.customer_name
          ? item.customer_name.toLowerCase()
          : '';
        const textTwo = item.tax_id ? item.tax_id.toLowerCase() : '';
        const textThree = item.email_id ? item.email_id.toLowerCase() : '';
        const textFour = item.mobile_no ? item.mobile_no.toLowerCase() : '';
        const textFifth = item.name.toLowerCase();
        const searchText = queryText.toLowerCase();
        const result = (
          textOne.indexOf(searchText) > -1 ||
          textTwo.indexOf(searchText) > -1 ||
          textThree.indexOf(searchText) > -1 ||
          textFour.indexOf(searchText) > -1 ||
          textFifth.indexOf(searchText) > -1
        );
        console.info('[Customer] customFilter result', { item, queryText, result });
        return result;
      } catch (error) {
        console.error('[Customer] Error in customFilter:', error);
        return false;
      }
    },
  },

  computed: {},

  created: function () {
    this.$nextTick(function () {
      try {
        console.info('[Customer] created hook');
        evntBus.on('register_pos_profile', (pos_profile) => {
          console.info('[Customer] register_pos_profile event', pos_profile);
          this.pos_profile = pos_profile;
          this.get_customer_names();
        });
        evntBus.on('payments_register_pos_profile', (pos_profile) => {
          console.info('[Customer] payments_register_pos_profile event', pos_profile);
          this.pos_profile = pos_profile;
          this.get_customer_names();
        });
        evntBus.on('set_customer', (customer) => {
          console.info('[Customer] set_customer event', customer);
          this.customer = customer;
        });
        evntBus.on('add_customer_to_list', (customer) => {
          console.info('[Customer] add_customer_to_list event', customer);
          this.customers.push(customer);
        });
        evntBus.on('set_customer_readonly', (value) => {
          console.info('[Customer] set_customer_readonly event', value);
          this.readonly = value;
        });
        evntBus.on('set_customer_info_to_edit', (data) => {
          console.info('[Customer] set_customer_info_to_edit event', data);
          this.customer_info = data;
        });
        evntBus.on('fetch_customer_details', () => {
          console.info('[Customer] fetch_customer_details event');
          this.get_customer_names();
        });
      } catch (error) {
        console.error('[Customer] Error in created hook:', error);
      }
    });
  },

  watch: {
    customer() {
      evntBus.emit('update_customer', this.customer);
    },
  },
};
</script>
