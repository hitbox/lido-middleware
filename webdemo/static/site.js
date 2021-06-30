function init() {
    let toggles = document.querySelectorAll("button[data-target]");
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
}

window.addEventListener("DOMContentLoaded", init);
