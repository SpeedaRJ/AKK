let counter = 0;

function check(el, solution) {
    if(solution) {
        el.style.border = "thick #00A881 dotted"
        counter++;
    } else {
        el.style.border = "thick #F15D2A dotted"
    }
    if(counter === 3) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}