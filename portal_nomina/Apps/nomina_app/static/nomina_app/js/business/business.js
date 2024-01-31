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

//-------------------- ajax func for data table ----------------------//

const dataSet = [
    ['Tiger Nixon', 'System Architect', 'Edinburgh', '5421', '2011/04/25', '$320,800'],
    ['Garrett Winters', 'Accountant', 'Tokyo', '8422', '2011/07/25', '$170,750'],
    ['Ashton Cox', 'Junior Technical Author', 'San Francisco', '1562', '2009/01/12', '$86,000'],
    ['Cedric Kelly', 'Senior Javascript Developer', 'Edinburgh', '6224', '2012/03/29', '$433,060'],
    ['Airi Satou', 'Accountant', 'Tokyo', '5407', '2008/11/28', '$162,700'],
    ['Brielle Williamson', 'Integration Specialist', 'New York', '4804', '2012/12/02', '$372,000'],
    ['Herrod Chandler', 'Sales Assistant', 'San Francisco', '9608', '2012/08/06', '$137,500'],
    ['Rhona Davidson', 'Integration Specialist', 'Tokyo', '6200', '2010/10/14', '$327,900'],
    ['Colleen Hurst', 'Javascript Developer', 'San Francisco', '2360', '2009/09/15', '$205,500'],
    ['Sonya Frost', 'Software Engineer', 'Edinburgh', '1667', '2008/12/13', '$103,600'],
    ['Jena Gaines', 'Office Manager', 'London', '3814', '2008/12/19', '$90,560'],
    ['Quinn Flynn', 'Support Lead', 'Edinburgh', '9497', '2013/03/03', '$342,000'],
    ['Charde Marshall', 'Regional Director', 'San Francisco', '6741', '2008/10/16', '$470,600'],
    ['Haley Kennedy', 'Senior Marketing Designer', 'London', '3597', '2012/12/18', '$313,500'],
    ['Tatyana Fitzpatrick', 'Regional Director', 'London', '1965', '2010/03/17', '$385,750'],
    ['Michael Silva', 'Marketing Designer', 'London', '1581', '2012/11/27', '$198,500'],
    ['Paul Byrd', 'Chief Financial Officer (CFO)', 'New York', '3059', '2010/06/09', '$725,000'],
    ['Gloria Little', 'Systems Administrator', 'New York', '1721', '2009/04/10', '$237,500'],
    ['Bradley Greer', 'Software Engineer', 'London', '2558', '2012/10/13', '$132,000'],
    ['Dai Rios', 'Personnel Lead', 'Edinburgh', '2290', '2012/09/26', '$217,500'],
    ['Jenette Caldwell', 'Development Lead', 'New York', '1937', '2011/09/03', '$345,000'],
    ['Yuri Berry', 'Chief Marketing Officer (CMO)', 'New York', '6154', '2009/06/25', '$675,000'],
    ['Caesar Vance', 'Pre-Sales Support', 'New York', '8330', '2011/12/12', '$106,450'],
    ['Doris Wilder', 'Sales Assistant', 'Sydney', '3023', '2010/09/20', '$85,600'],
    ['Angelica Ramos', 'Chief Executive Officer (CEO)', 'London', '5797', '2009/10/09', '$1,200,000'],
    ['Gavin Joyce', 'Developer', 'Edinburgh', '8822', '2010/12/22', '$92,575'],
    ['Jennifer Chang', 'Regional Director', 'Singapore', '9239', '2010/11/14', '$357,650'],
    ['Brenden Wagner', 'Software Engineer', 'San Francisco', '1314', '2011/06/07', '$206,850'],
    ['Fiona Green', 'Chief Operating Officer (COO)', 'San Francisco', '2947', '2010/03/11', '$850,000'],
    ['Shou Itou', 'Regional Marketing', 'Tokyo', '8899', '2011/08/14', '$163,000'],
    ['Michelle House', 'Integration Specialist', 'Sydney', '2769', '2011/06/02', '$95,400'],
    ['Suki Burks', 'Developer', 'London', '6832', '2009/10/22', '$114,500'],
    ['Prescott Bartlett', 'Technical Author', 'London', '3606', '2011/05/07', '$145,000'],
    ['Gavin Cortez', 'Team Leader', 'San Francisco', '2860', '2008/10/26', '$235,500'],
    ['Martena Mccray', 'Post-Sales support', 'Edinburgh', '8240', '2011/03/09', '$324,050'],
    ['Unity Butler', 'Marketing Designer', 'San Francisco', '5384', '2009/12/09', '$85,675'],
];
 
new DataTable('#users', {
    columns: [
        { title: 'RFC' },
        { title: 'Nombre' },
        { title: 'Usuario' },
        { title: 'Correos.' },
        { title: 'Estatus' },
        { title: 'Opciones' }
    ],
    data: dataSet
});
///
///var data = [
///    [
///        "Tiger Nixon",
///        "System Architect",
///        "Edinburgh",
///        "5421",
///        "2011/04/25",
///        "$3,120"
///    ],
///    [
///        "Garrett Winters",
///        "Director",
///        "Edinburgh",
///        "8422",
///        "2011/07/25",
///        "$5,300"
///    ]
///]
///
//$('#users').DataTable( {
//    data: dataSet
//} );


///resposive page tb
//responsive: {
//    details: {
//      display: $.fn.dataTable.Responsive.display.modal( {
//        header: function ( row ) {
//          var data = row.data();
//          return 'Detalles';
//        }
//      }),
//      renderer: function ( api, rowIdx, columns ) {
//        var data = $.map( columns, function ( col, i ) {
//          return '<tr>'+
//            '<td>'+col.title+':'+'</td> '+
//            '<td>'+col.data+'</td>'+
//          '</tr>';
//        } ).join('');
//        return $('<table class="table"/>').append( data );
//      }
//    }
//  },
//function dataSources ( rfc, nombre, usuario, correos, estatus, opciones ) {
//    this.rfc =rfc ;
//    this.nombre = nombre;
//    this.usuario = usuario;
//    this.correos= correos;
//    this.estatus = estatus;
//    this._opciones = opciones;
//    
// 
//    this.opciones = function () {
//        return this._opciones;
//    }
//};
// 
//$('#users').DataTable( {
//    data: [
//        new dataSources( "Tiger Nixon", "System Architect", "$3,120", "Edinburgh" ),
//        new dataSources( "Garrett Winters", "Director", "$5,400", "Edinburgh" ), 
//        new dataSources( "Garrett Winters", "Director", "$5,500", "Edinburgh" ), 
//        new dataSources( "Garrett Winters", "Director", "$5,600", "Edinburgh" ), 
//        new dataSources( "Garrett Winters", "Director", "$5,600", "Edinburgh" ), 
//        new dataSources( "Garrett Winters", "Director", "$5,700", "Edinburgh" )
//    ],
//    columns: [
//        { data: 'rfc' },
//        { data: 'nombre' },
//        { data: 'usuario' },
//        { data: 'correos' },
//        { data: 'estatus' },
//        { data: 'opciones' }
//    ]
//} );






//--------------MODALS-------------------------------------//


//
//DataTables warning: table id=users - Requested unknown parameter 'estatus' for row 0, column 4. For more //information about this error, please see https://datatables.net/tn/4
//


///// Example starter JavaScript for disabling form submissions if there are invalid fields
///(function () {
///    'use strict'
///    
///    // Fetch all the forms we want to apply custom Bootstrap validation styles to
///    var forms = document.querySelectorAll('.needs-validation')
///    
///    // Loop over them and prevent submission
///    Array.prototype.slice.call(forms)
///    .forEach(function (form) {
///    form.addEventListener('submit', function (event) {
///      if (!form.checkValidity()) {
///        event.preventDefault()
///        event.stopPropagation()
///      }
///    
///      form.classList.add('was-validated')
///    }, false)
///    })
///    })()
///    
///    
///    
///    //leading with the email sender while using inputs
///    // Select the buttons and input fields
///    const addEmailButton = document.getElementById("add-Email");
///    const removeEmailButton = document.getElementById("remove-Email");
///    const emailSenderInput = document.getElementById("email-sender");
///    const emailReceiverInput = document.getElementById("email-reciever");
///    
///    // Add event listeners to the buttons
///    addEmailButton.addEventListener("click", function() {
///    const emailToAdd = emailSenderInput.value.trim(); // Get email from sender input
///    
///    if (emailToAdd) {
///    // Append email to receiver input, handling existing emails
///    if (emailReceiverInput.value) {
///    emailReceiverInput.value += ", " + emailToAdd;
///    } else {
///    emailReceiverInput.value = emailToAdd;
///    }
///    
///    emailSenderInput.value = ""; // Clear sender input
///    }
///    });
///    
///    removeEmailButton.addEventListener("click", function() {
///    emailReceiverInput.value = ""; // Clear receiver input
///    });
///    
///    