
document.getElementById("clean-bt").addEventListener("click", function() {
    // Obtener todos los input y select del formulario
    const inputs = document.querySelectorAll("#panel-body-filter input, #panel-body-filter select");

    // Limpiar cada input y select
    inputs.forEach(function(input) {
      input.value = "";
    });

    // Reestablecer el select a la opción "Todos"
    document.getElementById("status").value = "";
  });


  // datepicker class 

  $(function () {
      $("#datepicker").datetimepicker({
          locale: "en",
          format: "DD MMMM YYYY",
          sideBySide: true
      });


  });

async function SendReport(){
    Swal.fire({
        title: "Would You like to generate a report?",
        text: "It would send it to your e-mail",
        icon: "info",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Yes, do it"
      }).then((result) => {
        if (result.isConfirmed) {
          Swal.fire({
            title: "Generated!",
            text: "Your file has been generated, check your e-mail.",
            icon: "success"
          });
        }
      });

}


async function SendCompt(){
    Swal.fire({
        title: "Download Files",
        text: "",
        icon: "info",
        html: `
        <style>
             .iconXml{
              font-size: 48px; 
              color:#099AFE;
            }
            .iconPdf{
              font-size: 48px; 
              color:#FE0909;
            }
        </style>
        <div class="d-flex justify-content-evenly"> 

              
                 <div class="col-md-3 ">

                  <h2>XMLS</h2>
                  <p><i class="bi bi-filetype-xml bi-3x iconXml"></i></p>
                  <input type="checkbox" id="vehicle1" name="vehicle1" value="Bike">
                  
                 </div>


                 <div class="col-md-3 ">

                  <h2>PDF</h2>
                  <p><i class="bi bi-filetype-pdf iconPdf"></i></i></p>
                  <input type="checkbox" id="" name="" value="">
                  
                 </div>

              </div>   
        `,
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Yes, download it!"
      }).then((result) => {
        if (result.isConfirmed) {
          Swal.fire({
            title: "Downloaded!",
            text: "Your file has been downloaded.",
            icon: "success"
          });
        }
      });

}


async function SendCompLP(){
    Swal.fire({
        title: "Are you sure?",
        text: "You won't be able to revert this!",
        icon: "info",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Yes, delete it!"
      }).then((result) => {
        if (result.isConfirmed) {
          Swal.fire({
            title: "Deleted!",
            text: "Your file has been deleted.",
            icon: "success"
          });
        }
      });

}



async function SendCompEmp(){
    Swal.fire({
        title: "Are you sure?",
        text: "You won't be able to revert this!",
        icon: "info",
        html: `
        <style>
             .iconXml{
              font-size: 48px; 
              color:#099AFE;
            }
            .iconPdf{
              font-size: 48px; 
              color:#FE0909;
            }
        </style>
        <div class="d-flex justify-content-evenly"> 

              
                 <div class="col-md-3 ">

                  <h2>XMLS</h2>
                  <p><i class="bi bi-filetype-xml bi-3x iconXml"></i></p>
                  <input type="checkbox" id="vehicle1" name="vehicle1" value="Bike">
                  
                 </div>


                 <div class="col-md-3 ">

                  <h2>PDF</h2>
                  <p><i class="bi bi-filetype-pdf iconPdf"></i></i></p>
                  <input type="checkbox" id="vehicle1" name="vehicle1" value="Bike">
                  
                 </div>

              </div>   
        `,
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Yes, delete it!"
      }).then((result) => {
        if (result.isConfirmed) {
          Swal.fire({
            title: "Downloaded!",
            text: "Your file has been downloaded.",
            icon: "success"
          });
        }
      });

}


async function SendPDF(){
    Swal.fire({
        title: "Would yopou like to generate a report?",
        text: "",
        icon: "info",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Yes, generete it!"
      }).then((result) => {
        if (result.isConfirmed) {
          Swal.fire({
            title: "Sended!",
            text: "Your file has been sended.",
            icon: "success",
            html: `
      
            <div> 
            <h3> The PDF file was started to be generated, once it is ready it will be sent by email to:<br> {e-mail}<br> 
            In case you have any error please contact technical support and specify the following id:<br>{id_report}</h3> 
              
            </div>   
        `,
          });
        }
      });

}



