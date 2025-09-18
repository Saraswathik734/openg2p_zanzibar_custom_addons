/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(ListController.prototype, {
    setup() {
        super.setup();
        this.action = useService("action");
        this.orm = useService("orm");
    },

    load_agency_wizard() {
        this.action.doAction({
            name: "Agency",
            type: "ir.actions.act_window",
            res_model: "g2p.agency",
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
            context: { create: false, agency_form_edit: true },
        });
        return window.location;
    },

    async load_warehouse_wizard() {
        const action = await this.orm.call("g2p.warehouse", "action_open_create_warehouse", [[]]);
        this.action.doAction(action);
        return window.location;
    },
    
    async load_sponsor_bank_wizard() {
        const action = await this.orm.call("g2p.warehouse", "action_open_create_sponsor_bank", [[]]);
        this.action.doAction(action);
        return window.location;
    },
    
    load_benefit_code_wizard() {
        this.action.doAction({
            name: "Benefit Codes",
            type: "ir.actions.act_window",
            res_model: "g2p.benefit.codes",
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
            context: { create: false, benefit_code_form_edit: true },
        });
        return window.location;
    },

    load_program_wizard() {
        this.action.doAction({
            name: "Program",
            type: "ir.actions.act_window",
            res_model: "g2p.program.definition",
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
            context: { create: false, program_form_edit: true, program_form_create: true },
        });
        return window.location;
    },

    load_region_wizard() {
        this.action.doAction({
            name: "Region",
            type: "ir.actions.act_window",
            res_model: "g2p.regions",
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
            context: { create: false, region_form_edit: true },
        });
        return window.location;
    },
});
