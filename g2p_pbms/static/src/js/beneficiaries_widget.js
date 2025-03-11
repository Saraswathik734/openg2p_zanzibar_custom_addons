/** @odoo-module **/

import { Component, useState, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

// Define the OWL component for beneficiaries.
export class G2PBeneficiariesComponent extends Component {
    static template = "g2p_beneficiaries_info_tpl";
    // static template = xml`

    // `;

    setup() {
        this.state = useState({
            title: _t("Beneficiaries"),
            records: [],
            page: 1,
            pageSize: 3,
            totalCount: 0,
            totalPages: 1,
        });
        this.orm = useService("orm");
        // this._fetchRecords();

    }

    async _fetchRecords() {
        // Call a server method to fetch beneficiaries data.
        const result = await this.orm.call(
            'g2p.eligibility.summary.wizard',
            'get_beneficiaries',
            [this.state.page, this.state.pageSize],
            {},
        );
        this.state.records = result.records;
        this.state.totalCount = result.total_count;
        this.state.totalPages = Math.ceil(result.total_count / this.state.pageSize) || 1;
    }

    async nextPage() {
        if (this.state.page < this.state.totalPages) {
            this.state.page++;
            await this._fetchRecords();
        }
    }

    async prevPage() {
        if (this.state.page > 1) {
            this.state.page--;
            await this._fetchRecords();
        }
    }
}

// Register the widget in the fields registry.
export const g2pBeneficiariesWidget = {
    component: G2PBeneficiariesComponent,
};
registry.category("fields").add("g2p_beneficiaries_widget", g2pBeneficiariesWidget);
