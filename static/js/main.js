"use strict";

// side navigation bar
function toggleSidebar() {
  document.getElementById("side-nav").classList.toggle("toggle-active");
  document.getElementById("main").classList.toggle("toggle-active");
  document.getElementById("top-navbar").classList.toggle("toggle-active");
  document.querySelector(".manage-wrap").classList.toggle("toggle-active");
}

// #################################
// popup

var c = 0;
function pop() {
  if (c == 0) {
    document.getElementById("popup-box").style.display = "block";
    c = 1;
  } else {
    document.getElementById("popup-box").style.display = "none";
    c = 0;
  }
}

// const popupMessagesButtons = document.querySelectorAll('popup-btn-messages')

// popupMessagesButtons.forEach(button, () => {
//     button.addEventListener('click', () => {
//         document.getElementById('popup-box-messages').style.display = 'none';
//     })
// })

// const popupMessagesButtom = document.getElementById('popup-btn-messages')
// popupMessagesButtom.addEventListener('click', () => {
//     document.getElementById('popup-box-messages').style.display = 'none';
// })
// ##################################

// Example starter JavaScript for disabling form submissions if there are invalid fields
// Fetch all the forms we want to apply custom Bootstrap validation styles to
var forms = document.getElementsByClassName("needs-validation");

// Loop over them and prevent submission
Array.prototype.filter.call(forms, function (form) {
  form.addEventListener(
    "submit",
    function (event) {
      if (form.checkValidity() === false) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add("was-validated");
    },
    false
  );
});
// ##################################

// extend and collapse
function showCourses(btn) {
  var btn = $(btn);

  if (collapsed) {
    btn.html('Collapse <i class="fas fa-angle-up"></i>');
    $(".hide").css("max-height", "unset");
    $(".white-shadow").css({ background: "unset", "z-index": "0" });
  } else {
    btn.html('Expand <i class="fas fa-angle-down"></i>');
    $(".hide").css("max-height", "150");
    $(".white-shadow").css({
      background: "linear-gradient(transparent 50%, rgba(255,255,255,.8) 80%)",
      "z-index": "2",
    });
  }
  collapsed = !collapsed;
}

$(document).ready(function () {
  $("#primary-search").focus(function () {
    $("#top-navbar").attr("class", "dim");
    $("#side-nav").css("pointer-events", "none");
    $("#main-content").css("pointer-events", "none");
  });
  $("#primary-search").focusout(function () {
    $("#top-navbar").removeAttr("class");
    $("#side-nav").css("pointer-events", "auto");
    $("#main-content").css("pointer-events", "auto");
  });

  // Initialize session timeout functionality if user is authenticated
  if (typeof window.userAuthenticated !== 'undefined' && window.userAuthenticated) {
    initSessionTimeout();
  }
});

// #################################
// Session Timeout Management
// #################################

let sessionTimeoutTimer;
let warningTimer;
let sessionTimeoutInterval;
let lastActivity = Date.now();
let warningShown = false;

// Activity tracking events
const activityEvents = [
  'mousedown', 'mousemove', 'keypress', 'scroll',
  'touchstart', 'click', 'keydown'
];

// Initialize session timeout functionality
function initSessionTimeout() {
  // Track user activity
  activityEvents.forEach(event => {
    document.addEventListener(event, resetActivityTimer, true);
  });

  // Check session status every 30 seconds
  sessionTimeoutInterval = setInterval(checkSessionStatus, 30000);

  // Initial session check
  checkSessionStatus();
}

// Reset activity timer on user interaction
function resetActivityTimer() {
  lastActivity = Date.now();
  warningShown = false;

  // Clear existing timers
  if (warningTimer) {
    clearTimeout(warningTimer);
  }
  if (sessionTimeoutTimer) {
    clearTimeout(sessionTimeoutTimer);
  }
}

// Check session status via AJAX
function checkSessionStatus() {
  $.ajax({
    url: '/ajax/session-timeout-check/',
    type: 'GET',
    success: function (response) {
      if (!response.authenticated) {
        // User is no longer authenticated, redirect to login
        window.location.href = '/login/';
        return;
      }

      // Update remaining time
      const remainingTime = response.remaining_time;
      const totalTimeout = response.total_timeout;

      // Update session status indicator
      updateSessionStatusIndicator(remainingTime, totalTimeout);

      // Show warning when 2 minutes remaining
      if (remainingTime <= 120 && !warningShown) {
        showSessionWarning(remainingTime);
        warningShown = true;
      }

      // Auto logout when time expires
      if (remainingTime <= 0) {
        logoutUser();
      }
    },
    error: function () {
      console.log('Session check failed');
      // Update indicator to show error state
      updateSessionStatusIndicator(0, 600, true);
    }
  });
}

// Update session status indicator in navbar
function updateSessionStatusIndicator(remainingTime, totalTimeout, error = false) {
  const indicator = $('#session-indicator');
  const timeDisplay = $('#session-time-display');

  if (error) {
    indicator.removeClass('text-success text-warning text-danger')
      .addClass('text-danger');
    timeDisplay.text('Error');
    return;
  }

  const minutes = Math.floor(remainingTime / 60);
  const seconds = Math.floor(remainingTime % 60);

  // Update indicator color based on remaining time
  indicator.removeClass('text-success text-warning text-danger');

  if (remainingTime > 300) { // More than 5 minutes
    indicator.addClass('text-success');
    timeDisplay.text(`${minutes}m`);
  } else if (remainingTime > 120) { // More than 2 minutes
    indicator.addClass('text-warning');
    timeDisplay.text(`${minutes}m`);
  } else { // Less than 2 minutes
    indicator.addClass('text-danger');
    timeDisplay.text(`${minutes}:${seconds.toString().padStart(2, '0')}`);
  }
}

// Show session timeout warning
function showSessionWarning(remainingTime) {
  // Create warning modal if it doesn't exist
  if (!$('#session-warning-modal').length) {
    const warningModal = `
      <div class="modal fade" id="session-warning-modal" tabindex="-1" aria-labelledby="sessionWarningModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content">
            <div class="modal-header bg-warning">
              <h5 class="modal-title" id="sessionWarningModalLabel">
                <i class="fas fa-exclamation-triangle me-2"></i>Session Timeout Warning
              </h5>
            </div>
            <div class="modal-body">
              <p>Your session will expire in <strong><span id="remaining-time">${Math.ceil(remainingTime)}</span> seconds</strong> due to inactivity.</p>
              <p>Click "Stay Logged In" to extend your session, or you will be automatically logged out.</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" id="logout-btn">
                <i class="fas fa-sign-out-alt me-1"></i>Logout Now
              </button>
              <button type="button" class="btn btn-primary" id="stay-logged-in-btn">
                <i class="fas fa-clock me-1"></i>Stay Logged In
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
    $('body').append(warningModal);
  }

  // Show the modal
  $('#session-warning-modal').modal({
    backdrop: 'static',
    keyboard: false
  });

  // Start countdown
  startCountdown(remainingTime);

  // Handle button clicks
  $('#stay-logged-in-btn').off('click').on('click', function () {
    extendSession();
    $('#session-warning-modal').modal('hide');
    warningShown = false;
  });

  $('#logout-btn').off('click').on('click', function () {
    logoutUser();
  });
}

// Start countdown in warning modal
function startCountdown(remainingTime) {
  let timeLeft = Math.ceil(remainingTime);
  const countdownElement = $('#remaining-time');

  const countdownInterval = setInterval(function () {
    timeLeft--;
    countdownElement.text(timeLeft);

    if (timeLeft <= 0) {
      clearInterval(countdownInterval);
      $('#session-warning-modal').modal('hide');
      logoutUser();
    }
  }, 1000);
}

// Extend session by making a request
function extendSession() {
  $.ajax({
    url: '/ajax/session-timeout-check/',
    type: 'GET',
    success: function (response) {
      if (response.authenticated) {
        resetActivityTimer();
        console.log('Session extended');
      }
    }
  });
}

// Logout user
function logoutUser() {
  // Clear all timers
  if (sessionTimeoutInterval) {
    clearInterval(sessionTimeoutInterval);
  }
  if (warningTimer) {
    clearTimeout(warningTimer);
  }
  if (sessionTimeoutTimer) {
    clearTimeout(sessionTimeoutTimer);
  }

  // Redirect to logout URL
  window.location.href = '/logout/';
}
