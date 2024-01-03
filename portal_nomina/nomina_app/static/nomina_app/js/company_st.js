
async function addCompany() {
    
      const { value: formValues } = await Swal.fire({
          title: "Add a Company",
          html: `
            <div class="container text-center" id="container">
              <div class ="row" id="row">
                <div class="col" id="col">
                  <input id="swal-input1" class="d-flex swal2-input">
                  <input id="swal-input2" class="float-start swal2-input">
                  <input id="swal-input3" class="float-end swal2-input">
                </div>
                  <input id="swal-input4" class="swal2-input">
                  <!--
                  <input id="swal-input5" class="swal2-input">
                  <input id="swal-input6" class="swal2-input">
                  <input id="swal-input7" class="swal2-input">
                  <input id="swal-input8" class="swal2-input">
                  <input id="swal-input9" class="swal2-input">
                  <input id="swal-input10" class="swal2-input">
                  <input id="swal-input11" class="swal2-input">
                  <input id="swal-input12" class="swal2-input">
                  <input id="swal-input13" class="swal2-input">
                  <input id="swal-input14" class="swal2-input">
                  <input id="swal-input15" class="swal2-input">
                  <input id="swal-input16" class="swal2-input">

                  -->
                  
            </div>
          `,
          focusConfirm: false,
          preConfirm: () => {
            return [
              
              document.getElementById("swal-input1").value,
              document.getElementById("swal-input2").value,
              document.getElementById("swal-input3").value,
              document.getElementById("swal-input4").value,
              //document.getElementById("swal-input5").value,
              //document.getElementById("swal-input6").value,
              //document.getElementById("swal-input7").value, 
              //document.getElementById("swal-input8").value,
              //document.getElementById("swal-input9").value,
              //document.getElementById("swal-input10").value,
              //document.getElementById("swal-input11").value,
              //document.getElementById("swal-input12").value,
              //document.getElementById("swal-input13").value,
              //document.getElementById("swal-input14").value,
              //document.getElementById("swal-input15").value, 
              //document.getElementById("swal-input16").value
            ];
          }
        });
        if (formValues) {
          Swal.fire(JSON.stringify(formValues));
        }

  // Reasignando la funcion al boton con el id 
  document.getElementById('addComp').addEventListener('click', addCompany);
}
      



async function frutas(){
const { value: estado } = await Swal.fire({
  title: "Select field validation",
  input: "select",
  inputOptions: {
    mexicoS:{  

      aguascalientes: "Aguascalientes",
      bajaCalifornia: "Baja California",
      baja_California_Sur: "Baja California Sur",
      campeche: "Campeche",
      Chiapas: "Chiapas",
      Chihuahua: "Chihuahua",
      CoahuilaZaragoza: "Coahuila de Zaragoza",
      Colima: "Colima",
      Durango: "Durango",
      EstadoMéxico: "Estado de México",
      Guanajuato: "Guanajuato",
      Guerrero: "Guerrero",
      Hidalgo: "Hidalgo",
      Jalisco: "Jalisco",
      Michoacán_Ocampo: "Michoacán de Ocampo",
      Morelos: "Morelos",
      Nayarit: "Nayarit",
      NuevoLeón: "Nuevo León",
      Oaxaca: "Oaxaca",
      Puebla: "Puebla",
      Querétaro: "Querétaro",
      QuintanaRoo: "Quintana Roo",
      San_Luis_Potosí: "San Luis Potosí",
      sinaloa: "Sinaloa",
      Sonora: "Sonora",
      Tabasco: "Tabasco",
      Tamaulipas: "Tamaulipas",
      Tlaxcala: "Tlaxcala",
      Veracruz: "Veracruz de Ignacio de la Llave",
      Yucatán: "Yucatán",
      Zacatecas: "Zacatecas"
    }
  },
  inputPlaceholder: "Select a state",
  showCancelButton: true,
  inputValidator: (value) => {
    return new Promise((resolve) => {
      if (value === "sinaloa") {
        resolve();
      } else {
        resolve("You need to select a state :)");
      }
    });
  }
});
if (estado) {
  Swal.fire(`You selected: ${estado}`);
}
}



function loadDoc() {
  const xhttp = new XMLHttpRequest();
  xhttp.onload = function() {
    document.getElementById("demo").innerHTML = this.responseText;
    }
  xhttp.open("GET", "ajax_info.txt", true);
  xhttp.send();
}


function mostrarFormulario() {
  // Crear una ventana emergente
  var popup = window.open('', 'Popup', 'width=400,height=300');

  // Crear un formulario dinámicamente dentro de la ventana emergente
  var form = document.createElement('form');
  form.id = 'popupForm';

  var labelNombre = document.createElement('label');
  labelNombre.textContent = 'Nombre:';
  form.appendChild(labelNombre);

  var inputNombre = document.createElement('input');
  inputNombre.type = 'text';
  inputNombre.name = 'nombre';
  form.appendChild(inputNombre);
  form.appendChild(document.createElement('br'));

  var labelEmail = document.createElement('label');
  labelEmail.textContent = 'Email:';
  form.appendChild(labelEmail);

  var inputEmail = document.createElement('input');
  inputEmail.type = 'email';
  inputEmail.name = 'email';
  form.appendChild(inputEmail);
  form.appendChild(document.createElement('br'));

  var submitButton = document.createElement('input');
  submitButton.type = 'submit';
  submitButton.value = 'Enviar';
  form.appendChild(submitButton);

  // Agregar el formulario al contenido de la ventana emergente
  popup.document.body.appendChild(form);

  // Manejar el envío del formulario (simulado con un console.log)
  form.addEventListener('submit', function(event) {
    event.preventDefault();
    console.log('Datos del formulario:', new FormData(form));
    // Puedes enviar los datos del formulario a tu servidor aquí

    // Cerrar la ventana emergente después de enviar el formulario
    popup.close();
  });
}






const openEls = document.querySelectorAll("[data-open]");
const closeEls = document.querySelectorAll("[data-close]");
const isVisible = "is-visible";

for (const el of openEls) {
  el.addEventListener("click", function() {
    const modalId = this.dataset.open;
    document.getElementById(modalId).classList.add(isVisible);
  });
}

for (const el of closeEls) {
  el.addEventListener("click", function() {
    this.parentElement.parentElement.parentElement.classList.remove(isVisible);
  });
}

document.addEventListener("click", e => {
  if (e.target == document.querySelector(".modal.is-visible")) {
    document.querySelector(".modal.is-visible").classList.remove(isVisible);
  }
});

document.addEventListener("keyup", e => {
  // if we press the ESC
  if (e.key == "Escape" && document.querySelector(".modal.is-visible")) {
    document.querySelector(".modal.is-visible").classList.remove(isVisible);
  }
});
