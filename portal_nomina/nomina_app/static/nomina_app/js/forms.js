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



document.addEventListener("DOMContentLoaded", function() {
    let choiceFormButton = document.getElementById("add_fields");
    let existingForm = document.getElementById("form-getChoice"); // Reemplaza con el ID de tu formulario existente

    choiceFormButton.addEventListener("click", function() {
        showSweetAlert();
    });



 function showSweetAlert() {
        let formHTML = `
            <form id="custom-form">
                <label for="inputField">Campo de entrada:</label>
                <input type="text" id="inputField" name="inputField">
            </form>`;

        Swal.fire({
            title: 'Agrega nuevas Opciones',
            html: formHTML,
            showCancelButton: true,
            confirmButtonText: 'Enviar',
            showLoaderOnConfirm: true,
            preConfirm: async (data_object) => {
                let inputFieldValue = document.getElementById('inputField').value;
                let data = new FormData();
                data.append("csrfmiddlewaretoken", getCookie("csrftoken"));
                data.append("inputField", inputFieldValue);

                try {
                    let response = await fetch(`/${pk}/choice/add/`, {
                        method: 'POST',
                        body: data,
                    });

                    if (!response.ok) {
                        throw new Error('La solicitud no se pudo completar');
                    }

                    

                    // Agrega los nuevos campos al formulario existente
                    const nuevoCampo = document.createElement('input');
                    nuevoCampo.type = 'text';
                    nuevoCampo.value = inputFieldValue;
                    
                    existingForm.appendChild(nuevoCampo);

                    return inputFieldValue;
                } catch (error) {
                    Swal.showValidationMessage(`Error: ${error}`);
                }
            },
            allowOutsideClick: () => !Swal.isLoading()
        })
        .then(result => {
            if (result.isConfirmed) {
                Swal.fire('Respuesta del servidor', result.value.message, 'success');
            }
        });
    }
});



  
  function messageAlert(){

    Swal.fire({
        icon: "error",
        title: "Oops...",
        text: "Something went wrong!",
        footer: '<a href="#">Why do I have this issue?</a>'
      });
  }