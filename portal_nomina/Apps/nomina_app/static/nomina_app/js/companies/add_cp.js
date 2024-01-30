let pk = window.location.pathname.substring(1, 3)
// script.js

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let token = getCookie("csrftoken");
console.log(token);

$(document).ready(function() {

    $("#add-cp").submit(function(event) {
        event.preventDefault();

        const formData = new FormData(this); // Use `this` to reference the form

        $.ajax({
            type: 'POST',
            url: '/dashboard/company/',
            data: formData,
            dataType: 'json',
            cache: false,
            contentType: false,
            processData: false
        })
        .done(function(response) {
            if (response.success) {
                window.location.replace("dashboard/");
            } else {
                // Use a more modern toast library for consistent styling
                toastr.error(response.message, 'Error');
            }
        })
        .fail(function(jqXHR, status, errorThrown) {
            console.error('AJAX error:', status, errorThrown); // Log error details
            toastr.error('An error occurred. Please try again.', 'Error');
        });
    });

    // Consider using a dedicated toast library for better styling and features
    function showAlert(message, alertType, timeout = 3000) {
        const $alert = $('<div class="alert alert-' + alertType + ' fade show" role="alert"><button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' + message + '</div>').appendTo('body');

        setTimeout(function() {
            $alert.alert('close');
        }, timeout);
    }
});
