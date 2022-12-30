document.addEventListener('DOMContentLoaded', () => {

  // Get all "navbar-burger" elements
  const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

  // Add a click event on each of them
  $navbarBurgers.forEach( el => {
    el.addEventListener('click', () => {

      // Get the target from the "data-target" attribute
      const target = el.dataset.target;
      const $target = document.getElementById(target);

      // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
      el.classList.toggle('is-active');
      $target.classList.toggle('is-active');

    });
  });

});

(function($) {
  $(".navbar-burger").on("click", function() {
      $(".navbar-burger").toggleClass("is-active");
      $(".navbar-menu").toggleClass("is-active");
  });

  let input = document.querySelector("#file-upload>.file-label>.file-input");

  if (input !== null) {
    input.onchange = function () {
      if (input.files.length > 0) {
        let fileNameContainer = document.querySelector(
          "#file-upload > .file-label>.file-name"
        );
        fileNameContainer.textContent = input.files[0].name;
      }
    }
  }
})(jQuery);
