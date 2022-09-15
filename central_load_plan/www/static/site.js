"use strict";

function getHREF(el) {
    /* walk up parents to get data-href attribute's value */
    let href;
    while (!(href = el.getAttribute("data-href"))) {
        el = el.parentElement;
    }
    return href
}

addEventListener("DOMContentLoaded", function() {
    for (const el of document.querySelectorAll("[data-href]")) {
        el.addEventListener("click", function(event) {
            switch (event.button) {
                case 0:
                    /* left click */
                    document.location = getHREF(event.target);
                    break;
                case 1:
                    /* middle click */
                    /* TODO: open in new tab does not work */
                    window.open(getHREF(event.target), "_blank");
                    break;
            }
        });
    }
});
