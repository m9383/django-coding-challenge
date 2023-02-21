<script setup>
</script>

<template>
  <h2>
    Expiring Licenses
  </h2>
  <div>
    <button @click="triggerEmailJob()">Trigger license expiry email job</button>
  </div>
  <br/><br/>
  <table>
      <tr>
          <th>Client</th>
          <th>Expiring License Count</th>
          <th>Notif sent</th>
      </tr>
      <tr v-for="notification in notifications">
        <td>{{ notification.client.client_name }}</td>
        <td>{{ notification.expiring_license_count }}</td>
        <td>{{ notification.created }}</td>
      </tr>
  </table>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      notifications: [],
    };
  },
  mounted() {
    this.triggerEmailJob();
  },

  methods: {
    async triggerEmailJob() {
      try {
        const response = await axios.post(
          "http://0.0.0.0:8000/api/v1/license/"
        );
        // JSON responses are automatically parsed.
        this.notifications = response.data;
      } catch (error) {
        console.log(error);
      }
    },
  },
};
</script>

<style scoped>
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}

table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}
</style>
