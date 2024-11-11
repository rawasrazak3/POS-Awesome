<template>
  <v-row justify="center">
    <v-dialog v-model="ticketDialog" max-width="800px" min-width="800px">
      <v-card>
        <v-card-title>
          <v-container>
            <v-row class="">
              <v-col cols="12" class="flex justify-between">
                <p class="headline primary--text">{{__('Tickets')}}</p>
              </v-col>
            </v-row>
          </v-container>
        </v-card-title>
        <v-container>
          <v-row>
            <!-- Display table only if there are items with count > 0 -->
            <v-col cols="12" class="pa-1" v-if="filtered_dialog_data.length">
              <v-data-table
                :headers="headers"
                :items="filtered_dialog_data"  
                item-key="name"
                class="elevation-1"
                v-model="selected"
              >
                <template v-slot:item.game="{ item }">
                  {{ item.game }}
                </template>
                <template v-slot:item.count="{ item }">
                  {{ item.count }}
                </template>
              </v-data-table>
            </v-col>
            <v-col cols="12" v-else>
              <p>{{ __('No tickets available') }}</p>
            </v-col>
          </v-row>
        </v-container>
        <v-card-actions class="mt-4">
          <v-spacer></v-spacer>
          <v-btn color="error mx-2" dark @click="close_dialog">Close</v-btn>
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
  data() {
    return {
      ticketDialog: false,  // Controls the dialog visibility
      headers: [
        { text: 'Game', value: 'game' },  // Adjust as per your object structure
        { text: 'Count', value: 'count' },  // Adjust as per your object structure
      ],
      dialog_data: [],  // Ensure it's an array
      selected: [],
    };
  },
  computed: {
    // Filter the dialog_data to show only items where count > 0
    filtered_dialog_data() {
      return this.dialog_data.filter(item => item.count > 0);
    }
  },
  methods: {
    close_dialog() {
      console.log('Dialog close called');
      this.ticketDialog = false;
    },
    submit_dialog() {
      console.log(this.selected);
    },
  },
  created() {
    evntBus.$on('open_ticket', (data) => {
      // Log to check the incoming data
      console.log('Received data:', data);

      // Ensure it's an array before assigning it to dialog_data
      if (Array.isArray(data)) {
        this.dialog_data = data;
        this.ticketDialog = true;
      } else {
        console.error('Expected an array but received:', data);
      }
    });
  }
};
</script>
