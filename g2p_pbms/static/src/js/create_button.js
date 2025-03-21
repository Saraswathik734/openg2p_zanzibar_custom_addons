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
            res_model: "g2p.agencies",
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
            context: { create: false, agency_form_edit: true },
        });
        return window.location;
    },

    load_delivery_classification_code_wizard() {
        this.action.doAction({
            name: "Delivery Classification Codes",
            type: "ir.actions.act_window",
            res_model: "g2p.delivery.classification.codes",
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
            context: { create: false, delivery_classification_code_form_edit: true },
        });
        return window.location;
    },

    load_delivery_code_wizard() {
        this.action.doAction({
            name: "Delivery Codes",
            type: "ir.actions.act_window",
            res_model: "g2p.delivery.codes",
            view_mode: "form",
            views: [[false, "form"]],
            target: "current",
            context: { create: false, delivery_code_form_edit: true },
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
            context: { create: false, program_form_edit: true },
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
