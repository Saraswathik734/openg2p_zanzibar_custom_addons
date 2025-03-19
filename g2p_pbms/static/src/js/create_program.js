/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(ListController.prototype, {
    setup() {
        super.setup();
        this.action = useService("action");
    },

    load_wizard() {
        var self = this;
        self.action.doAction({
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

});