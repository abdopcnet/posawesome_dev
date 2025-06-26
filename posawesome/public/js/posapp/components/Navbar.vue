<template>
  <nav>
    <v-app-bar app height="40" class="elevation-2">
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
        <span>{{ __('POS Awesome') }}</span>
      </v-toolbar-title>

      <v-spacer></v-spacer>
      <v-btn style="cursor: unset" variant="text" color="primary">
        <span right>{{ pos_profile.name }}</span>
      </v-btn>
      <div class="text-center">
        <v-menu offset="y">
          <template v-slot:activator="{ props }">
            <v-btn color="primary" dark variant="text" v-bind="props">
              {{ __('Menu') }}
            </v-btn>
          </template>
          <v-card class="mx-auto" max-width="300" tile>
            <v-list density="compact" v-model="menu_item">
              <v-list-item
                @click="close_shift_dialog"
                v-if="!pos_profile.posa_hide_closing_shift && menu_item == 0"
              >
                <v-icon class="mr-2">mdi-content-save-move-outline</v-icon>
                <span>{{ __('Close Shift') }}</span>
              </v-list-item>
              <v-list-item
                @click="print_last_invoice"
                v-if="pos_profile.posa_allow_print_last_invoice && this.last_invoice"
              >
                <v-icon class="mr-2">mdi-printer</v-icon>
                <span>{{ __('Print Last Receipt') }}</span>
              </v-list-item>
              <v-divider class="my-0"></v-divider>
              <v-list-item @click="logOut">
                <v-icon class="mr-2">mdi-logout</v-icon>
                <span>{{ __('Logout') }}</span>
              </v-list-item>
              <v-list-item @click="go_about">
                <v-icon class="mr-2">mdi-information-outline</v-icon>
                <span>{{ __('About') }}</span>
              </v-list-item>
            </v-list>
          </v-card>
        </v-menu>
      </div>
    </v-app-bar>
    <v-navigation-drawer
      v-model="drawer"
      :mini-variant.sync="mini"
      app
      class="primary margen-top"
      width="170"
    >
      <v-list>
        <v-list-item class="px-2">
          <v-avatar>
            <v-img :src="company_img"></v-img>
          </v-avatar>
          <span class="ml-2">{{ company }}</span>
          <v-btn icon @click.stop="mini = !mini">
            <v-icon>mdi-chevron-left</v-icon>
          </v-btn>
        </v-list-item>
        <v-list v-model="item">
          <v-list-item
            v-for="(listItem, index) in items"
            :key="listItem.text"
            @click="changePage(listItem.text)"
          >
            <v-icon class="mr-2">{{ listItem.icon }}</v-icon>
            <span>{{ listItem.text }}</span>
          </v-list-item>
        </v-list>
      </v-list>
    </v-navigation-drawer>
    <v-snackbar v-model="snack" :timeout="5000" :color="snackColor" top right>
      {{ snackText }}
    </v-snackbar>
    <v-dialog v-model="freeze" persistent max-width="290">
      <v-card>
        <v-card-title class="text-h5">{{ freezeTitle }}</v-card-title>
        <v-card-text>{{ freezeMsg }}</v-card-text>
      </v-card>
    </v-dialog>
  </nav>
</template>

<script>
import { evntBus } from '../bus';

export default {
  // components: {MyPopup},
  data() {
    return {
      drawer: false,
      mini: true,
      item: 0,
      items: [
        { text: 'POS', icon: 'mdi-network-pos' },
        { text: 'Payments', icon: 'mdi-credit-card' }
      ],
      page: '',
      fav: true,
      menu: false,
      message: false,
      hints: true,
      menu_item: 0,
      snack: false,
      snackColor: '',
      snackText: '',
      company: 'Andalus Sweets',
      company_img: '/assets/erpnext/images/erpnext-logo.svg',
      pos_profile: '',
      freeze: false,
      freezeTitle: '',
      freezeMsg: '',
      last_invoice: '',
    };
  },
  methods: {
    changePage(key) {
      console.info('[Navbar] changePage called', key);
      this.$emit('changePage', key);
    },
    go_desk() {
      console.info('[Navbar] go_desk called');
      frappe.set_route('/');
      location.reload();
    },
    go_about() {
      console.info('[Navbar] go_about called');
      const win = window.open(
        'https://github.com/yrestom/POS-Awesome',
        '_blank'
      );
      win.focus();
    },
    close_shift_dialog() {
      console.info('[Navbar] close_shift_dialog called');
      evntBus.emit('open_closing_dialog');
    },
    show_mesage(data) {
      console.info('[Navbar] show_mesage called', data);
      this.snack = true;
      this.snackColor = data.color;
      this.snackText = data.text;
    },
    logOut() {
      console.info('[Navbar] logOut called');
      var me = this;
      me.logged_out = true;
      return frappe.call({
        method: 'logout',
        callback: function (r) {
          if (r.exc) {
            console.error('[Navbar] Error during logout', r.exc);
            return;
          }
          frappe.set_route('/login');
          location.reload();
        },
      });
    },
    print_last_invoice() {
      console.info('[Navbar] print_last_invoice called', this.last_invoice);
      if (!this.last_invoice) return;
      const print_format =
        this.pos_profile.print_format_for_online ||
        this.pos_profile.print_format;
      const letter_head = this.pos_profile.letter_head || 0;
      const url =
        frappe.urllib.get_base_url() +
        '/printview?doctype=Sales%20Invoice&name=' +
        this.last_invoice +
        '&trigger_print=1' +
        '&format=' +
        print_format +
        '&no_letterhead=' +
        letter_head;
      const printWindow = window.open(url, 'Print');
      printWindow.addEventListener(
        'load',
        function () {
          printWindow.print();
        },
        true
      );
    },
  },
  created: function () {
    this.$nextTick(function () {
      try {
        console.info('[Navbar] created hook');
        evntBus.on('show_mesage', (data) => {
          console.info('[Navbar] show_mesage event', data);
          this.show_mesage(data);
        });
        evntBus.on('set_company', (data) => {
          console.info('[Navbar] set_company event', data);
          this.company = data.name;
          this.company_img = data.company_logo
            ? data.company_logo
            : this.company_img;
        });
        evntBus.on('register_pos_profile', (data) => {
          console.info('[Navbar] register_pos_profile event', data);
          this.pos_profile = data.pos_profile;
          const payments = { text: 'Payments', icon: 'mdi-cash-register' };
          if (
            this.pos_profile.posa_use_posa_pos_awesome_payments &&
            this.items.length !== 2
          ) {
            this.items.push(payments);
          }
        });
        evntBus.on('set_last_invoice', (data) => {
          console.info('[Navbar] set_last_invoice event', data);
          this.last_invoice = data;
        });
        evntBus.on('freeze', (data) => {
          console.info('[Navbar] freeze event', data);
          this.freeze = true;
          this.freezeTitle = data.title;
          this.freezeMsg = data.msg;
        });
        evntBus.on('unfreeze', () => {
          console.info('[Navbar] unfreeze event');
          this.freeze = false;
          this.freezTitle = '';
          this.freezeMsg = '';
        });
      } catch (error) {
        console.error('[Navbar] Error in created hook:', error);
      }
    });
  },
};
</script>

<style scoped>
.margen-top {
  margin-top: 0px;
}
</style>