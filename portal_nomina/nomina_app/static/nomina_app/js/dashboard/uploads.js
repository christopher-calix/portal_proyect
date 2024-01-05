const image = window.django.static('nomina_app/static/nomina_app/img/zipIcon.png');

        // Función para ocultar el boton de submit al iniciar la pagina
        $(document).ready(function() {
            $("#sender").hide(); // Oculta el botón al cargar la página
          });

        // Función para manejar la carga de archivos
        function handleFileUpload(input) {
            var uploadedFileContainer = document.getElementById('uploaded-file');
            var file = input.files[0];
    
            // Muestra el nombre del archivo en el contenedor
            uploadedFileContainer.innerHTML = '<div class="card" style="width: 18rem;"><div class="card-body"><svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"viewBox="0 0 512 512" style="enable-background:new 0 0 512 512;" xml:space="preserve"><g id="_x34_6_x5F_Zip"><g id="XMLID_4668_"><path id="XMLID_4677_" style="fill:#7878C8;" d="M165,399.863V247.538c0-4.419,4.255-7.538,8.674-7.538H414V81h-65c-4.418,0-9-3.581-9-8V0H98v447h316v-39H173.674C169.255,408,165,404.281,165,399.863z M140,40h142c4.418,0,8,3.582,8,8
                   s-3.582,8-8,8H140c-4.419,0-8-3.582-8-8S135.581,40,140,40z M140,89h142c4.418,0,8,3.581,8,8s-3.582,8-8,8H140
                   c-4.419,0-8-3.581-8-8S135.581,89,140,89z M140,140h234c4.418,0,8,3.581,8,8s-3.582,8-8,8H140c-4.419,0-8-3.581-8-8
                   S135.581,140,140,140z M132,198c0-4.419,3.581-8,8-8h234c4.418,0,8,3.581,8,8s-3.582,8-8,8H140C135.581,206,132,202.419,132,198z"
                   />
               <path id="XMLID_4676_" style="fill:#7878C8;" d="M82,455V89H25v423h323v-49H91C86.581,463,82,459.418,82,455z"/>
               <polygon id="XMLID_4675_" style="fill:#7878C8;" points="356,9.914 356,65 407.689,65 		"/>
               <path id="XMLID_4674_" style="fill:#FB7949;" d="M410.624,298H401v18h9.624c4.922,0,8.926-4.079,8.926-9
                   C419.55,302.079,415.546,298,410.624,298z"/>
               <path id="XMLID_4669_" style="fill:#FB7949;" d="M181,256v136h305V256H181z M291,348c4.418,0,8,3.582,8,8s-3.582,8-8,8h-41.164
                   c-2.905,0-5.583-1.575-6.993-4.115c-1.411-2.539-1.334-5.645,0.201-8.111L277.749,296H249c-4.419,0-8-3.582-8-8s3.581-8,8-8
                   h43.149c2.905,0,5.582,1.575,6.993,4.115c1.411,2.539,1.334,5.645-0.201,8.111L264.236,348H291z M357,348c4.418,0,8,3.582,8,8
                   s-3.582,8-8,8h-33c-4.418,0-8-3.582-8-8s3.582-8,8-8h8v-52h-8c-4.418,0-8-3.582-8-8s3.582-8,8-8h33c4.418,0,8,3.582,8,8
                   s-3.582,8-8,8h-9v52H357z M410.624,332H401v25.55c0,4.418-3.582,8-8,8s-8-3.582-8-8v-67.7c0-4.418,4.281-7.85,8.699-7.85h16.925
                   c13.744,0,24.926,11.256,24.926,25C435.55,320.744,424.368,332,410.624,332z"/>
           </g>
       </g>
       <g id="Layer_1">
       </g>
       </svg><p class="card-text">' + file.name +'</p></div></div>';
    
            // Puedes agregar estilos adicionales o lógica según tus necesidades
            uploadedFileContainer.style.border = '1px dashed #ccc';
          
            uploadedFileContainer.style.padding = '10px';
            uploadedFileContainer.style.borderRadius = '10px';  // Cambia el valor '10px' según tus preferencias


             // Obtén el valor del input de tipo file
             var archivo = document.getElementById("file-upload").value;
      
             // Obtén el botón
             var boton = document.getElementById("sender");
       
             // Verifica si el campo de archivo está vacío
             if (archivo === "") {
               // Si está vacío, desactiva el botón y ocúltalo
               boton.hide();
                boton.prop("disabled", true); // Desactiva el botón si está vací
               
             } else {
               // Si contiene algo, activa el botón y muéstralo
               boton.disabled = false;
               boton.show();
             }

        }

