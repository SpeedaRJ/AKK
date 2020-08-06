function checkTabPress(e) {
    "use strict";
    e = e || event;
    if (e.keyCode == 9 || e.keyCode == 13) {
        $('input.textarea').each(function() {
            if ( this.value === '' ) {
                this.focus();
                return false;
            }
        })
    }
}

$(function(){
    document.querySelector('body').addEventListener('keyup', checkTabPress);
})