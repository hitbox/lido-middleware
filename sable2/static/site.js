"use strict";

window.addEventListener("DOMContentLoaded", function() {
    let toggles = document.querySelectorAll("button.toggle[data-target]");
    for (let i = 0; i < toggles.length; i++) {
        toggles[i].addEventListener("click", function() {
            let target = this.getAttribute("data-target");
            target = document.getElementById(target);
            if (target.style.display === 'none') {
                target.style.display = '';
            } else {
                target.style.display = 'none';
            }
        });
    }

    let copyButtons = document.querySelectorAll("button.copy");
    console.log(copyButtons);
    for (let i = 0; i < copyButtons.length; i++) {
        copyButtons[i].addEventListener("click", function() {
            let source = this.getAttribute("data-source");
            source = document.getElementById(source);
            navigator.clipboard.writeText(source.innerHTML);
        });
    }

});
