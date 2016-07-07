/**
 * Javascript Library used in WAVES generated forms
 * @Author: Marc Chakiachvili
 * @License: MIT
 * @Version: 1.0
 */

/**
 * Serviceform class constructor, used as
 * @constructor
 */
var ServiceForm = function(form){
    this.form = form;
    console.log('Form is ' + this.form + ' length' + this.form.elements.length);
};

/**
 *
 * @param source
 * @param condition
 * @param target
 */
ServiceForm.prototype.conditionnal = function(source, target){
    source.onselect = function(){
        console.log('on select called');
    }
};

/**
 * Attach a sample to a Form Element (mainly FileInputs)
 * @param source Form Element to attach sample radio button
 * @param sample Sample descriptor (mainly server side file)
 */
ServiceForm.prototype.sample = function(source, sample){
    sample.onclick = function(){
        console.log('Sample is clicked');
    };
};

