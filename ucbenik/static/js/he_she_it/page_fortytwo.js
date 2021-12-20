let solutions = [
    ["am"],
    ["wear", "have"],
    ["have"],
    ["am"],
    ["is"],
    ["has"],
    ["has", "wears"],
    ["is"],
    ["has"],
    ["is"],
    ["are"],
    ["are"],
]

function solution(el, n) {
    console.log('^' + solutions[n].join().toLowerCase() + '\\.*\\!*\\?*$')
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^' + solutions[n].join('|').toLowerCase() + '\\.*\\!*\\?*$')) {
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else {
        el.classList.add("incorrect");
        el.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("textarea")
    let counter = 0;
    for (let x in paras) {
        if (paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    if (counter === solutions.length)
        document.getElementById("next").removeAttribute("disabled")
    else
        document.getElementById("next").setAttribute("disabled", "disabled");
}
