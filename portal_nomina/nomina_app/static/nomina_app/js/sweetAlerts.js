
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



function template(){

  const myCustomHTML = `
  <template id="my-template">
  <swal-title>
    Save changes to "Untitled 1" before closing?
  </swal-title>
  <swal-icon type="warning" color="red"></swal-icon>
  <swal-button type="confirm">
    Save As
  </swal-button>
  <swal-button type="cancel">
    Cancel
  </swal-button>
  <swal-button type="deny">
    Close without Saving
  </swal-button>
  <swal-param name="allowEscapeKey" value="false" />
  <swal-param
    name="customClass"
    value='{ "popup": "my-popup" }' />
  <swal-function-param
    name="didOpen"
    value="popup => console.log(popup)" />
  </template>
`;

  Swal.fire({
    template: "#my-template"
  });
  
  
  document.getElementById('addComp').addEventListener('click', template);

}
