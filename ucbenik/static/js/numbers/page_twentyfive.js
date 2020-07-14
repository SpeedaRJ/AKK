let numbers = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
    "twenty",
    "twenty-one",
    "twenty-two",
    "twenty-three",
    "twenty-four",
    "twenty-five",
    "twenty-six",
    "twenty-seven",
    "twenty-eight",
    "twenty-nine",
    "thirty",
    "thirty-one",
    "thirty-two",
    "thirty-three",
    "thirty-four",
    "thirty-five",
    "thirty-six",
    "thirty-seven",
    "thirty-eight",
    "thirty-nine",
    "forty",
    "forty-one",
    "forty-two",
    "forty-three",
    "forty-four",
    "forty-five",
    "forty-six",
    "forty-seven",
    "forty-eight",
    "forty-nine",
    "fifty",
    "fifty-one",
    "fifty-two",
    "fifty-three",
    "fifty-four",
    "fifty-five",
    "fifty-six",
    "fifty-seven",
    "fifty-eight",
    "fifty-nine",
    "sixty",
    "sixty-one",
    "sixty-two",
    "sixty-three",
    "sixty-four",
    "sixty-five",
    "sixty-six",
    "sixty-seven",
    "sixty-eight",
    "sixty-nine",
    "seventy",
    "seventy-one",
    "seventy-two",
    "seventy-three",
    "seventy-four",
    "seventy-five",
    "seventy-six",
    "seventy-seven",
    "seventy-eight",
    "seventy-nine",
    "eighty",
    "eighty-one",
    "eighty-two",
    "eighty-three",
    "eighty-four",
    "eighty-five",
    "eighty-six",
    "eighty-seven",
    "eighty-eight",
    "eighty-nine",
    "ninety",
    "ninety-one",
    "ninety-two",
    "ninety-three",
    "ninety-four",
    "ninety-five",
    "ninety-six",
    "ninety-seven",
    "ninety-eight",
    "ninety-nine",
    "one hundred"
]

function toOrigin(el) {
    var origin = document.getElementById('drag-origin');
    if (origin === el.parentElement) return;
    let drop = document.getElementById('dominos').children[0];
    let placeholder = document.getElementById('placeholder');
    drop.insertBefore(placeholder,el);
    origin.appendChild(el);
    el.classList.remove('connected');
    el.style="";
    el.children[0].classList.remove('incorrect');
    el.children[0].classList.remove('correct');
    checkCorrectness();
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("Text", ev.target.id);
}


function drop(ev, el) {
    var origin = document.getElementById('drag-origin');
    let placeholder = document.getElementById('placeholder')
    ev.preventDefault();
    var data = ev.dataTransfer.getData("Text");
    correct = data.search(el.id.replace("0","")) > -1;
    var child = document.getElementById(data);
    let last=parseInt(child.id[child.id.length-1]);
    el.classList.add('full');
    el.insertBefore(child,placeholder);
    placeholder.remove();
    let children = el.children
    for(var i = 0; i < children.length; i++) {
        children[i].classList.add("connected");
        children[i].style.marginLeft=(8*i)+"vh";
    }
    children[0].style.marginTop="2vh";
    el.innerHTML+='<div class="domino connected" id="placeholder"></div>';
    checkCorrectness();
}

function evaluate(el) {
    var origin = document.getElementById('drag-origin');
    if (origin === el.parentElement) return;
    let sibling = el.previousElementSibling;
    numberELement = el.children[0]
    try {
        if(numbers[parseInt(numberELement.innerText)] == sibling.children[1].innerText) {
            numberELement.classList.remove('incorrect');
            numberELement.classList.add('correct');
        } else {
            numberELement.classList.remove('correct');
            numberELement.classList.add('incorrect');
        }
    } catch(e) {
        numberELement.classList.remove('incorrect');
        numberELement.classList.remove('correct');
    }
}

function checkCorrectness() {
    let dominos = document.getElementsByClassName('domino');
    Array.from(document.getElementsByClassName("domino")).forEach(function(item) {
        if(item.id != "first" && item.id != "placeholder")
            evaluate(item);
    });
    let items = document.getElementsByClassName("domino-part")
    let counter = 0;
    for(let x = 0; x < items.length; x++) {
        if(items[x].classList !== undefined && items[x].className.includes("correct") && !items[x].className.includes("incorrect"))
            counter++;
    }
    if(counter === 5) {
        document.getElementById("next").removeAttribute("disabled")
    } else {
         document.getElementById("next").setAttribute("disabled", "disabled");
    }
}


function redo(e) {
    Array.from(document.getElementsByClassName("domino")).forEach(function(item) {
        if(item.id != "first" && item.id != "placeholder")
            toOrigin(item);
    });
    var origin= document.getElementById('drag-origin');
    shuffle(origin);
    let ns = [];
    for(i=0; i < 5; i++) {
        var n = Math.round(Math.random() * 100);
        while(ns.includes(n)) 
            n = Math.round(Math.random() * 100);
        ns.push(n);
        d=i+1;
        let word = numbers[n];
        document.getElementById("d"+d+"1").innerHTML='<span>'+word+'</span>';
        document.getElementById("d"+d+"2").innerHTML='<span>'+n+'</span>';
    }
    document.getElementById("d6").innerHTML='<span>'+numbers[Math.round(Math.random() * 100)]+'</span>';
}


$(function () {
    redo();
});

function shuffle(el) {
    if(el.children == 0) return;
    for (var i = el.children.length; i >= 0; i--) {
        el.appendChild(el.children[Math.random() * i | 0]);
    }
}
