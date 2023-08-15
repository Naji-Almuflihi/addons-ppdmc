odoo.define('bi_partial_payment_invoice.account_payment', function (require) {
"use strict";

    // const { patch } = require('web.utils');    
    // const PaymentRegistry = require("account.payment");
    // console.log('PaymentRegistry-------',PaymentRegistry)
    // const rpc = require('web.rpc');
    // const core = require('web.core');
    // const _t = core._t;


    // patch(PaymentRegistry.ShowPaymentLineWidget.prototype,'bi_partial_payment_invoice.account_payment', {
    //     async assignOutstandingCredit(id) {
    //         console.log('this.props======>',this.props)
    //         const value = this.props.value;
            
    //         var data = await rpc.query({model: 'ir.ui.view',
    //                     method: 'get_view_id',
    //                     args: ["bi_partial_payment_invoice.account_payment_wizard_form"],});
            
    //         this.action.doAction({
    //             name: _t('Payment Wizard'),
    //             type: 'ir.actions.act_window',
    //             view_mode: 'form',
    //             res_model: 'account.payment.wizard',
    //             context: {
    //                 payment_value : value,
    //                 line_id : id
    //                 },
    //             views: [[data[1], 'form']],
    //             target : 'new'
    //         });
    //     },
    //     async removeMoveReconcile(moveId, partialId) {
    //         console.log('partialId-------',partialId)
    //         await rpc.query({model: 'account.partial.reconcile',
    //             method: 'unlink',
    //             args: [partialId],
    //             context: {'move_id': moveId,'from_js':true}
    //             }
    //         )
    //         location.reload();
                
                

    //         // var paymentId = parseInt($(event.target).attr('payment-id'));
    //         // console.log('paymentId======>.',paymentId)
    //     }

    // })

    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var field_utils = require('web.field_utils');
    var payment = require('account.payment');
    var QWeb = core.qweb;
    var _t = core._t;

    var ShowPaymentLineWidget = payment.ShowPaymentLineWidget;


    ShowPaymentLineWidget.include({

        init: function() {
            var self = this;
            this._super.apply(this, arguments);
        },

        start: function () {
            var self = this;
            return this._super();
        },

        _onOutstandingCreditAssign: function (event) {
                event.stopPropagation();
                event.preventDefault();
                var self = this;
                var id = $(event.target).data('id') || false;
                var value = JSON.parse(this.value);
                this._rpc({
                    model: 'ir.model.data',
                    method: 'xmlid_to_res_model_res_id',
                    args: ["bi_partial_payment_invoice.account_payment_wizard_form"],
                }).then(function (data) {
                    self.do_action({
                        name: _t('Payment Wizard'),
                        type: 'ir.actions.act_window',
                        view_mode: 'form',
                        res_model: 'account.payment.wizard',
                        context: {
                            payment_value : value,
                            line_id : id
                        },
                        views: [[data[1], 'form']],
                        target : 'new'
                    });
                });
            },

        // _onRemoveMoveReconcile: function (event) {
        //     var self = this;
        //     var paymentId = parseInt($(event.target).attr('payment-id'));

        //     if (paymentId !== undefined && !isNaN(paymentId)){
        //         console.log('THIS==========>',this,paymentId)
        //         console.log('EVENt===========',event)
        //         this._rpc({
        //             model: 'account.partial.reconcile',
        //             method: 'remove_partial_reconcile',
        //             args: [[]],
        //             context: {'move_id': this.res_id,'from_js':true,line_id:paymentId},
        //         }).then(function () {
        //             self.trigger_up('reload');
        //         });
        //     }
        // },
    });

});