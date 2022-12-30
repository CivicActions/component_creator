const headers = document.getElementsByClassName("accordion-header"),
      contents = document.getElementsByClassName("accordion-content"),
      icons = document.getElementsByClassName("accordion-icon");

for (let i = 0; i < headers.length; i++) {
     headers[i].addEventListener("click", () => {

          for (let j = 0; j < contents.length; j++) {
               if (i == j) {
                    let iconName = contents[j].getBoundingClientRect().height === 0 ? "remove-outline" : "add-outline";
                    icons[j].setAttribute("name", iconName)
                    contents[j].classList.toggle("accordion-content-transition");
               } else {
                    icons[j].innerHTML = "+";
                    contents[j].classList.remove("accordion-content-transition");
               }
          }

     });
}
