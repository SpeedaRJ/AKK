let objects1 = [
    "row0",
    "row1",
    "row2",
    "row3",
    "row4",
    "row5",
    "row6",
    "row7",
    "row8",
    "row9",
    "row10",
    "row11",
    "row12",
    "row13",
    "row14",
    "row15",
    "row16",
    "row17",
    "row18",
    "row19",
]

let objects2 = [
    "row112",
    "row122",
    "row132",
    "row142",
    "row152",
    "row162",
    "row172",
    "row182",
    "row192",
]

let firstSolved = false;


function redo(e) {
    shuffle(objects1);
    /* hide all objects */
    for (i = 0; i < objects1.length; i++) {
        let obj = document.getElementById(objects1[i]);
        obj.style.display = "none";
        children = obj.children;
        children[0].classList.remove("incorrect");
        children[0].classList.remove("correct");
        children[1].classList.remove("incorrect");
        children[1].classList.remove("correct");
    }

    for (i = 0; i < 5; i++) {
        let obj = document.getElementById(objects1[i]);
        obj.style.display = "block";
        children = obj.children;
        children[0].classList.remove("incorrect");
        children[0].classList.remove("correct");
        children[1].classList.remove("incorrect");
        children[1].classList.remove("correct");
        if (Math.random() > 0.5) {
            children[0].children[0].style.display = "none";
            children[0].children[1].style.display = "inline";
            children[1].children[0].style.display = "inline";
            children[1].children[1].style.display = "none";
            children[0].children[0].value = '';
            children[0].children[1].value = '';
            children[1].children[0].value = '';
            children[1].children[1].value = '';
        } else {
            children[0].children[1].style.display = "none";
            children[0].children[0].style.display = "inline";
            children[1].children[1].style.display = "inline";
            children[1].children[0].style.display = "none";
            children[0].children[0].value = '';
            children[0].children[1].value = '';
            children[1].children[0].value = '';
            children[1].children[1].value = '';
        }
    }
}

function redo2(e) {
    shuffle(objects2);
    /* hide all objects */
    for (i = 0; i < objects2.length; i++) {
        let obj = document.getElementById(objects2[i]);
        obj.style.display = "none";
        children = obj.children;
        children[0].classList.remove("incorrect");
        children[0].classList.remove("correct");
        children[1].classList.remove("incorrect");
        children[1].classList.remove("correct");
    }

    for (i = 0; i < 5; i++) {
        let obj = document.getElementById(objects2[i]);
        obj.style.display = "block";
        children = obj.children;
        children[0].classList.remove("incorrect");
        children[0].classList.remove("correct");
        children[1].classList.remove("incorrect");
        children[1].classList.remove("correct");
        if (Math.random() > 0.5) {
            children[0].children[0].style.display = "none";
            children[0].children[1].style.display = "inline";
            children[1].children[0].style.display = "inline";
            children[1].children[1].style.display = "none";
            children[0].children[0].value = '';
            children[0].children[1].value = '';
            children[1].children[0].value = '';
            children[1].children[1].value = '';
        } else {
            children[0].children[1].style.display = "none";
            children[0].children[0].style.display = "inline";
            children[1].children[1].style.display = "inline";
            children[1].children[0].style.display = "none";
            children[0].children[0].value = '';
            children[0].children[1].value = '';
            children[1].children[0].value = '';
            children[1].children[1].value = '';
        }
    }
}

function shuffle(a) {
    var j, x, i;
    for (i = a.length - 1; i > 0; i--) {
        j = Math.floor(Math.random() * (i + 1));
        x = a[i];
        a[i] = a[j];
        a[j] = x;
    }
    return a;
}

function solution(el, solution) {
    let parent = el.parentElement;
    if (el.value.toLowerCase().trim().replace(/  +/g, ' ').match('^' + solution + '\\.*\\!*$')) {
        parent.classList.remove("incorrect");
        parent.classList.add("correct");
    } else {
        parent.classList.add("incorrect");
        parent.classList.remove("correct");
    }
    let paras = document.getElementsByClassName("tip")
    let counter = 0;
    for (let x in paras) {
        if (paras[x].classList !== undefined && paras[x].className.includes("correct") && !paras[x].className.includes("incorrect"))
            counter++;
    }
    console.log(counter)
    var next = document.getElementById("next");
    if (counter == 5) {
        next.setAttribute('onclick', "display2()");
        next.removeAttribute("disabled");
        firstSolved = true;
    } else if (counter == 10 || counter == 5 && firstSolved) {
        next.setAttribute('onclick', "window.location.href='/lesson_one/numbers/page_thirteen'");
        next.removeAttribute("disabled");
    } else {
        next.setAttribute("disabled", "disabled");
    }
}

function display2() {
    document.getElementById("table1").style.display = "none";
    document.getElementById("table2").style.display = "block";
}


$(function () {
    redo();
    redo2();
})