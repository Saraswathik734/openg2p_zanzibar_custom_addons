/** @odoo-module **/
import { CharField } from "@web/views/fields/char/char_field";
import { registry } from "@web/core/registry";
import { onWillUpdateProps, useState } from "@odoo/owl";


export class DeliveryUnitWidget extends CharField {
    static template = "g2p_pbms.DeliveryUnitWidget";

    setup() {
        super.setup();
        console.log("THIS:", this)
        this.state = useState({
            record_data: this.props.record.data,
        });
        // onWillUpdateProps((nextProps) => {
        //     this.delivery_type = nextProps.record.data.delivery_type;
        // });
        // console.log("THIS2:", this)
        // this.delivery_type = this.props.record.data.delivery_type;

        this.currencyOptions = [
            { value: "USD", label: "USD" },
            { value: "EUR", label: "EUR" },
            { value: "GBP", label: "GBP" },
            { value: "JPY", label: "JPY" },
            // Add more ISO codes as needed.
        ];
    }




}

registry.category("fields").add("g2p_pbms.delivery_unit_widget", {
    component: DeliveryUnitWidget,
});
