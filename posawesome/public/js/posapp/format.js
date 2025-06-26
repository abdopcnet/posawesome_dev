export default {
    data () {
        return {
            float_precision: 2,
            currency_precision: 2
        };
    },
    methods: {
        flt (value, precision, number_format, rounding_method) {
            try {
                console.info('[format.js] flt called', { value, precision, number_format, rounding_method });
                if (!precision && precision != 0) {
                    precision = this.currency_precision || 2;
                }
                if (!rounding_method) {
                    rounding_method = "Banker's Rounding (legacy)";
                }
                return flt(value, precision, number_format, rounding_method);
            } catch (error) {
                console.error('[format.js] Error in flt:', error);
                return value;
            }
        },
        formatCurrency (value, precision) {
            try {
                console.info('[format.js] formatCurrency called', { value, precision });
                const format = get_number_format(this.pos_profile?.currency);
                value = format_number(
                    value,
                    format,
                    precision || this.currency_precision || 2
                );
                return value;
            } catch (error) {
                console.error('[format.js] Error in formatCurrency:', error);
                return value;
            }
        },
        formatFloat (value, precision) {
            try {
                console.info('[format.js] formatFloat called', { value, precision });
                const format = get_number_format(this.pos_profile.currency);
                value = format_number(value, format, precision || this.float_precision || 2);
                return value;
            } catch (error) {
                console.error('[format.js] Error in formatFloat:', error);
                return value;
            }
        },
        setFormatedCurrency (el, field_name, precision, no_negative = false, $event) {
            let value = 0;
            try {
                console.info('[format.js] setFormatedCurrency called', { el, field_name, precision, no_negative, $event });
                // make sure it is a number and positive
                let _value = parseFloat($event.target.value);
                if (!isNaN(_value)) {
                    value = _value;
                }
                if (no_negative && value < 0) {
                    value = value * -1;
                }
                value = this.formatCurrency($event.target.value, precision);
            } catch (e) {
                console.error('[format.js] Error in setFormatedCurrency:', e);
                value = 0;
            }
            // check if el is an object
            if (typeof el === "object") {
                el[field_name] = value;
            }
            else {
                this[field_name] = value;
            }
            return value;
        },
        setFormatedFloat (el, field_name, precision, no_negative = false, $event) {
            let value = 0;
            try {
                console.info('[format.js] setFormatedFloat called', { el, field_name, precision, no_negative, $event });
                // make sure it is a number and positive
                value = parseFloat($event.target.value);
                if (isNaN(value)) {
                    value = 0;
                } else if (no_negative && value < 0) {
                    value = value * -1;
                }
                value = this.formatFloat($event.target.value, precision);
            } catch (e) {
                console.error('[format.js] Error in setFormatedFloat:', e);
                value = 0;
            }
            // check if el is an object
            if (typeof el === "object") {
                el[field_name] = value;
            }
            else {
                this[field_name] = value;
            }
            return value;
        },
        currencySymbol (currency) {
            try {
                console.info('[format.js] currencySymbol called', currency);
                return get_currency_symbol(currency);
            } catch (error) {
                console.error('[format.js] Error in currencySymbol:', error);
                return '';
            }
        },
        isNumber (value) {
            try {
                console.info('[format.js] isNumber called', value);
                const pattern = /^-?(\d+|\d{1,3}(\.\d{3})*)(,\d+)?$/;
                return pattern.test(value) || "invalid number";
            } catch (error) {
                console.error('[format.js] Error in isNumber:', error);
                return false;
            }
        }
    },
    mounted () {
        this.float_precision =
            frappe.defaults.get_default('float_precision') || 2;
        this.currency_precision =
            frappe.defaults.get_default('currency_precision') || 2;
    }
};