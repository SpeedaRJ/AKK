openSubmenus = [false, false, false, false, false];

$(function () {
  let buttonsLeft = document
    .getElementById("Menu")
    .querySelectorAll("button:not(.titleB)");

  buttonsLeft.forEach((element) => {
    element.addEventListener("click", colorButtons(buttonsLeft));
  });

  let buttonsRight = document
    .getElementById("Dicts")
    .querySelectorAll("button");

  buttonsRight.forEach((element) => {
    element.addEventListener("click", colorButtons(buttonsRight));
  });

  let mainMenu = document
    .getElementById("Menu")
    .querySelectorAll("button:not(.titleB):not(.SB):not(.dictB)");
  mainMenu.forEach((element) => {
    element.addEventListener("click", openSubmenu(mainMenu));
  });
});

function colorButtons(buttons) {
  return function (event) {
    buttons.forEach((element) => {
      if (
        element != event.currentTarget &&
        element.innerHTML !== "Glossary" &&
        element.className !== "SB"
      ) {
        element.style.cssText = "background-color: #6699CC";
      } else if (element.innerHTML === "Glossary") {
        element.style.cssText = "background-color: #3E83D5";
      } else if (element.className === "SB") {
        element.style.cssText = "background-color: #4b5385";
      }
    });
    event.currentTarget.style.cssText = "background-color: #EBC35C";
  };
}

function openSubmenu(buttons) {
  return function (event) {
    if (!openSubmenu[event.currentTarget.innerHTML.split(" ")[1] - 1]) {
      event.currentTarget.parentNode.querySelectorAll("ul")[0].style.cssText =
        "display: block";
      openSubmenu[event.currentTarget.innerHTML.split(" ")[1] - 1] = true;
    } else {
      event.currentTarget.parentNode.querySelectorAll("ul")[0].style.cssText =
        "display: none";
      openSubmenu[event.currentTarget.innerHTML.split(" ")[1] - 1] = false;
    }
    buttons.forEach((element) => {
      if (
        element !== event.currentTarget &&
        openSubmenu[element.innerHTML.split(" ")[1] - 1] == true
      ) {
        element.parentNode.querySelectorAll("ul")[0].style.cssText =
          "display: none";
        openSubmenu[element.innerHTML.split(" ")[1] - 1] = false;
      }
    });
  };
}
