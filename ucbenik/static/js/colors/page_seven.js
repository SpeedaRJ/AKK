let colors = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Pink", "Black", "Grey", "White", "Brown", "Gold", "Silver"];
let hex_codes = ["#EE202E", "#F26524", "#F7ED38", "#099E43", "#3097C3", "#7A2A90", "#EF509C", "#231F20", "#85837D", "#F8F8F8", "#653614", "#FBAD18", "#B6B2AC"];
let answers = [];

function solution(el) {
    if(el.value.toLowerCase() === answers[el.parentNode.id.slice(-1) - 1].toLowerCase()) {
        el.classList.remove("incorrect");
        el.classList.add("correct");
    } else {
        el.classList.add("incorrect");
        el.classList.remove("correct");
    }
    checkCorrectness();
}

function setColors() {
    let selected = [];
    while (selected.length !== 5) {
        let randomElement = colors[Math.floor(Math.random() * colors.length)];
        if(!selected.includes(randomElement)) selected.push(randomElement);
    }
    let hex = [];
    for(let color in selected) {
        hex.push(hex_codes[colors.findIndex((element) => element === selected[color])]);
        answers.push(selected[color]);
    }
    document.getElementById("color01").style.backgroundColor = hex[0];
    document.getElementById("color02").style.backgroundColor = hex[1];
    document.getElementById("color03").style.backgroundColor = hex[2];
    document.getElementById("color04").style.backgroundColor = hex[3];
    document.getElementById("color05").style.backgroundColor = hex[4];
}

function redo(e) {
    answers = [];
    setColors();
    let node = [].slice.call(document.getElementsByClassName("answer"));
    [].forEach.call(node, function(el) {el.value = ""; el.classList.remove("correct"); el.classList.remove("incorrect");});
    checkCorrectness();
}

function checkCorrectness() {
    let items = document.getElementsByClassName("answer")
    let counter = 0;
    for(let x = 0; x < items.length; x++) {
        if(items[x].classList !== undefined && items[x].className.includes("correct") && !items[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === items.length) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}

$(function () {
    setColors();
});
