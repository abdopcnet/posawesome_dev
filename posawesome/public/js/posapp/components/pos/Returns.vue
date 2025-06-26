<template>
  <v-row justify="center">
    <v-dialog v-model="invoicesDialog" max-width="800px" min-width="800px">
      <v-card>
        <v-card-title>
          <span class="headline primary--text">{{ __('Return Invoice') }}</span>
        </v-card-title>
        <v-container>
          <v-row class="mb-4">
            <v-text-field
              color="primary"
              :label="__('Invoice Number')"
              background-color="white"
              hide-details
              v-model="invoice_name"
              dense
              clearable
              class="mx-4"
              @keydown.enter="search_invoices"
            ></v-text-field>
            <v-btn text class="ml-2" color="primary" dark @click="search_invoices">
              {{ __('Search') }}
            </v-btn>
          </v-row>
          <v-row>
            <v-col cols="12" class="pa-1">
              <v-data-table
                :headers="headers"
                :items="dialog_data"
                item-value="name"
                class="elevation-1"
                show-select
                v-model="selected"
                :loading="isLoading"
                loading-text="Loading invoices..."
                no-data-text="No invoices found"
              >
                <template v-slot:[`item.grand_total`]="{ item }">
                  {{ currencySymbol(item.currency) }} {{ formatCurrency(item.grand_total) }}
                </template>
              </v-data-table>
            </v-col>
          </v-row>
        </v-container>
        <v-card-actions class="mt-4">
          <v-spacer></v-spacer>
          <v-btn color="error mx-2" dark @click="close_dialog">{{ __('Close') }}</v-btn>
          <v-btn color="success" dark @click="submit_dialog">
            {{ __('Select') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-row>
</template>

<script>
import { evntBus } from '../../bus';
import format from '../../format';

export default {
  mixins: [format],
  data: () => ({
    invoicesDialog: false,
    selected: [],
    dialog_data: [],
    isLoading: false,
    company: '',
    invoice_name: '',
    pos_profile: null,
    pos_opening_shift: null,
    headers: [
      { title: __('Customer'), key: 'customer', align: 'start', sortable: true },
      { title: __('Date'), key: 'posting_date', align: 'start', sortable: true },
      { title: __('Invoice'), key: 'name', align: 'start', sortable: true },
      { title: __('Amount'), key: 'grand_total', align: 'end', sortable: false }
    ]
  }),
  beforeUnmount() {
    evntBus.off('open_returns');
  },
  methods: {
    close_dialog() {
      console.info('[Returns] close_dialog called');
      this.$nextTick(() => {
        this.invoicesDialog = false;
        this.selected = [];
        this.dialog_data = [];
        this.invoice_name = '';
      });
    },
    search_invoices() {
      console.info('[Returns] search_invoices called', { invoice_name: this.invoice_name, company: this.company });
      // Always set company from latest pos_profile or pos_opening_shift if available
      this.company = this.pos_profile?.company || this.pos_opening_shift?.company || this.company;
      if (!this.company && !this.invoice_name) {
        console.error('[Returns] No company or invoice_name provided');
        evntBus.emit('show_mesage', {
          text: __('Please enter an invoice number or select a company first'),
          color: 'error'
        });
        return;
      }
      this.isLoading = true;
      frappe.call({
        method: 'posawesome.posawesome.api.posapp.search_invoices_for_return',
        args: {
          invoice_name: this.invoice_name,
          company: this.company
        },
        callback: (r) => {
          this.isLoading = false;
          if (r.message) {
            console.info('[Returns] search_invoices result', r.message);
            this.dialog_data = r.message.map(item => ({
              name: item.name,
              customer: item.customer,
              posting_date: item.posting_date,
              grand_total: item.grand_total,
              currency: item.currency,
              items: item.items || []
            }));
          }
        },
        error: (err) => {
          this.isLoading = false;
          console.error('[Returns] Error in search_invoices:', err);
          evntBus.emit('show_mesage', {
            text: __('Failed to search invoices'),
            color: 'error'
          });
        }
      });
    },
    async submit_dialog() {
      console.info('[Returns] submit_dialog called', { selected: this.selected });
      if (!this.selected.length || !this.dialog_data.length) {
        console.error('[Returns] No invoice selected or dialog_data empty');
        evntBus.emit('show_mesage', {
          text: __('Please select a valid invoice'),
          color: 'error'
        });
        return;
      }
      const selectedItem = this.dialog_data.find(item => item.name === this.selected[0]);
      if (!selectedItem) {
        console.error('[Returns] Selected invoice not found in dialog_data');
        return;
      }
      const return_doc = selectedItem;
      // جلب الفاتورة الأصلية من السيرفر
      let original_invoice = null;
      try {
        const response = await frappe.call({
          method: 'frappe.client.get',
          args: {
            doctype: "Sales Invoice",
            name: return_doc.name
          }
        });
        original_invoice = response.message;
        console.info('[Returns] Original invoice fetched', original_invoice);
      } catch (e) {
        console.error('[Returns] Error fetching original invoice:', e);
        evntBus.emit('show_mesage', {
          text: __('Failed to fetch original invoice'),
          color: 'error'
        });
        return;
      }
      if (!original_invoice) {
        console.error('[Returns] Original invoice not found');
        evntBus.emit('show_mesage', {
          text: __('Original invoice not found'),
          color: 'error'
        });
        return;
      }
      const original_items = original_invoice.items.map(i => i.item_code);
      const invalid_items = return_doc.items.filter(item => !original_items.includes(item.item_code));
      if (invalid_items.length > 0) {
        console.error('[Returns] Invalid items in return_doc:', invalid_items);
        evntBus.emit('show_mesage', {
          text: __('The following items do not exist in the original invoice: {0}', invalid_items.map(i => i.item_code)),
          color: 'error'
        });
        return;
      }
      // حفظ الكائنات كاملة في المستند
      const invoice_doc = {
        items: return_doc.items.map(item => ({
          ...item,
          qty: item.qty * -1,
          stock_qty: item.stock_qty * -1,
          amount: item.amount * -1
        })),
        is_return: 1,
        company: (this.pos_opening_shift && this.pos_opening_shift.company) || (this.pos_profile && this.pos_profile.company) || '',
        customer: return_doc.customer,
        posa_pos_opening_shift: this.pos_opening_shift?.name,
        pos_opening_shift: this.pos_opening_shift || null, // حفظ الكائن كامل
        pos_profile: this.pos_profile || null // حفظ الكائن كامل
      };
      console.info('[Returns] Emitting load_return_invoice', { invoice_doc, return_doc });
      evntBus.emit('load_return_invoice', { invoice_doc, return_doc });
      this.invoicesDialog = false;
    }
  },
  created() {
    console.info('[Returns] created hook');
    evntBus.on('open_returns', (data) => {
      console.info('[Returns] open_returns event', data);
      this.invoicesDialog = true;
      this.pos_profile = data.pos_profile || null;
      this.pos_opening_shift = data.pos_opening_shift || null;
      // Always set company from pos_profile or pos_opening_shift
      this.company = (this.pos_profile && this.pos_profile.company) || (this.pos_opening_shift && this.pos_opening_shift.company) || '';
      this.dialog_data = [];
      this.selected = [];
      // Fetch initial invoices
      frappe.call({
        method: 'frappe.client.get_list',
        args: {
          doctype: 'Sales Invoice',
          filters: { company: this.company },
          fields: ['name', 'customer', 'posting_date', 'grand_total', 'currency']
        },
        callback: (response) => {
          console.info('[Returns] Initial invoices loaded', response.message);
          this.dialog_data = response.message;
        },
        error: (err) => {
          console.error('[Returns] Error loading initial invoices:', err);
          evntBus.emit('show_mesage', {
            text: __('Failed to load invoices'),
            color: 'error'
          });
        }
      });
    });
  }
};
</script>

<style scoped>
.v-data-table {
  font-size: 0.875rem;
}
</style>