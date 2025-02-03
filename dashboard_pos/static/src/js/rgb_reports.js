/** @odoo-module **/
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";
import { Component } from "@odoo/owl";
import { onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
const actionRegistry = registry.category("actions");

export class RgbReports extends Component{
    setup() {
        super.setup(...arguments);
        this.orm = useService('orm')
        this.user = useService("user");
        this.actionService = useService("action");
        this.state = useState({
            journal_balance : [],
            mrp_dashboard_data : [],
        });
        // When the component is about to start, fetch data in tiles
        onWillStart(async () => {
            await this.fetch_data();
            await this.fetch_data_mrp();
        });

        onMounted(async () => {
            await this.onclick_mrp_search()
        });

    }

    async fetch_data() {
        var data =  await this.orm.call('account.journal','rgb_get_bank_cash_dashboard_data',[])
            this.state.journal_balance = data['journal_balance']
    }

    FormatDate(dateStr) {
        var date = new Date(dateStr); // Parse the date string into a Date object
        var year = date.getFullYear();
        var month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-based
        var day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`; // Return in YYYY-MM-DD format
    }
    async onclick_mrp_search(events) {
        const self = this;
        let date_from = $('#mrp_date_from').val();
        let date_to = $('#mrp_date_to').val();

        // Validate and set default dates if necessary
        if (!date_from || !date_to) {
            const date = new Date();
            const year = date.getFullYear();
            date_from = `${year}-01-01`; // Start of the year
            date_to = `${year}-12-31`;   // End of the year
        }

        // Ensure dates are properly formatted (assuming FormatDate is defined)
        date_from = this.FormatDate(date_from);
        date_to = this.FormatDate(date_to);

        try {
            // Fetch data from the server
            const data = await this.orm.call('rgb.reports', 'get_mrp_dashboard_data', [], { date_from, date_to });
            console.log('Fetched Data:', data);

            // Update state with the fetched data
            this.state.mrp_dashboard_data = data['mrp_dashboard_data'];

            // Trigger a re-render if necessary (depends on your framework)
            this.render(); // Example: Call render if your framework requires it
        } catch (error) {
            console.error('Error fetching MRP dashboard data:', error);
            // Handle the error (e.g., show a notification to the user)
        }
    }
    async fetch_data_mrp() {
        await this.onclick_mrp_search()
    }
}
RgbReports.template = 'RgbReports'
registry.category("actions").add("rgb_report_menu", RgbReports)