/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

export class G2PBeneficiariesComponent extends Component {
    static template = "g2p_beneficiaries_info_tpl";

    setup() {
        this.state = useState({
            title: _t("Beneficiaries"),
            records: [],
            page: 1,
            pageSize: 3,
            totalCount: 0,
            totalPages: 1,
            target_registry: null,
            searched: false,  // initially hidden title and pagination
            searchQuery: "",  // bound to the search input
        });
        this.orm = useService("orm");
    }

    searchRegistrants() {
        this.state.searched = true;  // show title and pagination when search is clicked
        this.state.page = 1;
        this.state.pageSize = 20;
        this.state.target_registry = this.props.record.data.target_registry;
        this.state.list_workflow_status = this.props.record.data.list_workflow_status;
        this._fetchRecords();
    }

    fetchDisbursementDetails(bridge_disbursement_id) {
        
    }

    async _fetchRecords() {
        const result = await this.orm.call(
            'g2p.eee.summary.wizard',
            'get_beneficiaries',
            [this.props.record.resId , this.state.page, this.state.pageSize],
            {},
        );
        if (result.message) {
            this.state.records = result.message.beneficiaries;
            this.state.totalCount = result.message.total_beneficiary_count;
        } else {
            this.state.records = result.records;
            this.state.totalCount = result.total_count;
        }
        this.state.totalPages = Math.ceil(this.state.totalCount / this.state.pageSize) || 1;
        this.state.target_registry = this.props.record.data.target_registry;
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

export const g2pBeneficiariesWidget = {
    component: G2PBeneficiariesComponent,
};
registry.category("fields").add("g2p_beneficiaries_widget", g2pBeneficiariesWidget);
