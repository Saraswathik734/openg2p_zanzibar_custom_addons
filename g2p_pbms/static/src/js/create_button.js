/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(ListController.prototype, {
    setup() {
        super.setup();
        this.action = useService("action");
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

    load_warehouse_wizard() {
        this.action.doAction({
            name: "Warehouse",
            type: "ir.actions.act_window",
            res_model: "g2p.warehouse",
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
            context: { create: false, warehouse_form_edit: true },
        });
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
