// navbar
window.addEventListener("DOMContentLoaded", (event) => {
  var navbarShrink = function () {
    const navbarCollapsible = document.body.querySelector("#mainNav");
    if (!navbarCollapsible) {
      return;
    }
    if (window.scrollY === 0) {
      navbarCollapsible.classList.remove("navbar-shrink");
    } else {
      navbarCollapsible.classList.add("navbar-shrink");
    }
  };

  navbarShrink();

  document.addEventListener("scroll", navbarShrink);

  const mainNav = document.body.querySelector("#mainNav");
  if (mainNav) {
    new bootstrap.ScrollSpy(document.body, {
      target: "#mainNav",
      rootMargin: "0px 0px -40%",
    });
  }
});

// small screen profile dropdown
document.addEventListener("DOMContentLoaded", function () {
  if (window.innerWidth < 992) {
    document
      .querySelectorAll(".navbar .dropdown")
      .forEach(function (everydropdown) {
        everydropdown.addEventListener("hidden.bs.dropdown", function () {
          this.querySelectorAll(".submenu").forEach(function (everysubmenu) {
            everysubmenu.style.display = "none";
          });
        });
      });
  }
});

// search bar
document.querySelector("#search-input").addEventListener("input", filterList);

function filterList() {
  const searchInput = document.querySelector("#search-input");
  const filter = searchInput.value.toLowerCase();
  const listItems = document.querySelectorAll(".mylist-item");

  listItems.forEach((item) => {
    let text = item.textContent;
    if (text.toLowerCase().includes(filter.toLowerCase())) {
      item.style.display = "";
    } else {
      item.style.display = "none";
    }
  });
}

// detail destinations
function next() {
  let lists = $('.item')
  $("#slide").append(lists[0]);
  
};

function prev() {
  let lists = $('.item')
  $("#slide").prepend(lists[lists.length - 1]);
  
};

function sign_out() {
  $.removeCookie("mytoken", { path: "/" });
  alert("Signed out!");
  window.location.href = "/";
}