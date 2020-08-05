function check(el, solution) {
    if(solution) {
        if (el.className.includes("right"))
            el.classList.remove("right")
        else
            el.classList.add("right")
    } else {
        if (el.className.includes("wrong"))
            el.classList.remove("wrong")
        else
            el.classList.add("wrong")
    }
    checkrightness();
}

function checkrightness() {
    items = document.getElementsByTagName('input');
    let counter = 0;
    for(let x = 0; x < items.length; x++) {
        if(items[x].classList !== undefined && items[x].className.includes("right"))
            counter++;
        if (items[x].classList !== undefined && items[x].className.includes("wrong"))
            counter--
    }
    if(counter === 3) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}