var index = 0;
var lists = ["first","second","third"];

function changelist() {
     index++;
     if(index == 2){
        document.getElementById("next-list").setAttribute("disabled", "disabled");
        document.getElementById("next").removeAttribute("disabled");
     }
     document.getElementById(lists[index - 1]).setAttribute("hidden", "hidden");
     document.getElementById(lists[index]).removeAttribute("hidden");
}