<template>
  <v-app class="container1">
    <v-main>
      <Navbar @changePage="setPage($event)"></Navbar>
      <component :is="page" class="mx-4 md-4"></component>
    </v-main>
  </v-app>
</template>

<script>
import Navbar from './components/Navbar.vue';
import POS from './components/pos/Pos.vue';
import Payments from './components/payments/Pay.vue';

export default {
  data: function () {
    return {
      page: 'POS',
    };
  },
  components: {
    Navbar,
    POS,
    Payments,
  },
  methods: {
    setPage(page) {
      console.info('[Home] setPage called', page);
      this.page = page;
    },
    remove_frappe_nav() {
      try {
        console.info('[Home] remove_frappe_nav called');
        this.$nextTick(function () {
          $('.page-head').remove();
          $('.navbar.navbar-default.navbar-fixed-top').remove();
        });
      } catch (error) {
        console.error('[Home] Error in remove_frappe_nav:', error);
      }
    },
  },
  mounted() {
    try {
      console.info('[Home] mounted hook');
      this.remove_frappe_nav();
    } catch (error) {
      console.error('[Home] Error in mounted hook:', error);
    }
  },
  updated() {
    try {
      console.info('[Home] updated hook');
    } catch (error) {
      console.error('[Home] Error in updated hook:', error);
    }
  },
  created: function () {
    try {
      console.info('[Home] created hook');
      setTimeout(() => {
        this.remove_frappe_nav();
      }, 1000);
    } catch (error) {
      console.error('[Home] Error in created hook:', error);
    }
  },
};
</script>

<style scoped>
.container1 {
  margin-top: 0px;
}
</style>
