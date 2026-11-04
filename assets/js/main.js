/* HOMIYA — site interactions. Vanilla JS, zero dependencies. */

// Current year in footer
document.addEventListener("DOMContentLoaded", function () {
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();

  // Mobile nav toggle
  var toggle = document.getElementById("navToggle");
  var links = document.getElementById("navLinks");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("open");
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { links.classList.remove("open"); });
    });
  }

  // Inquiry form -> Web3Forms (free, no backend). Replace access_key in HTML.
  var form = document.getElementById("inquiryForm");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = document.getElementById("formStatus");
      var data = new FormData(form);
      status.textContent = "Sending…";
      status.className = "form-status";
      fetch("https://api.web3forms.com/submit", {
        method: "POST",
        body: data
      })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (res.success) {
            status.textContent = "Thanks! We received your inquiry and will reply within 1 business day.";
            status.className = "form-status ok";
            form.reset();
          } else {
            status.textContent = "Something went wrong. Please email Yvonnehome2026@outlook.com directly.";
            status.className = "form-status err";
          }
        })
        .catch(function () {
          status.textContent = "Network error. Please email Yvonnehome2026@outlook.com directly.";
          status.className = "form-status err";
        });
    });
  }
});
