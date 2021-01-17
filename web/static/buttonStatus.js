// $(function() {
//     $('#blankCheckbox').select(function() {
// console.log("Hello");
//     });
// });

// $(document).ready(function(){
//     console.log("Hi");
//       $('#blankCheckbox').change(function(){
//         console.log("Hi");
//           var val = $('#blankCheckbox').val();
//             console.log(val)
//           if (val == '') {
//               $('#assignOrders').attr('disabled', 'disabled');
//           }else{
//               $('#assignOrders').removeAttr('disabled');
//           }
//       });
//   });

$(document).ready(function () {
  var markedCheckbox = document.querySelectorAll('input[type="checkbox"]:checked');
  if (markedCheckbox.length == 0) {
    $('#assignOrders').attr('disabled', 'disabled');
    $('#deleteOrders').attr('disabled', 'disabled');
    
  }
  else{
    $('#assignOrders').removeAttr('disabled');
    $('#deleteOrders').removeAttr('disabled');
  }
});

jQuery(function(){
  if (localStorage.input) {
      var checks = JSON.parse(localStorage.input);
      jQuery(':checkbox').prop('checked', function(i) {
          return checks[i];
      });
  }
});

$(document).on("change", "input[name='checkbox']", function () {

  console.log("hello");
  var markedCheckbox = document.querySelectorAll('input[type="checkbox"]:checked');
  console.log(markedCheckbox);
  console.log(markedCheckbox.length == 0)
  if (markedCheckbox.length == 0) {
    $('#assignOrders').attr('disabled', 'disabled');
    $('#deleteOrders').attr('disabled', 'disabled');
  }
  else {
    $('#assignOrders').removeAttr('disabled');
    $('#deleteOrders').removeAttr('disabled');
  }
});


// $(document).on('click', '.checkbox', function() {
//   console.log("hello");
//   var markedCheckbox = document.querySelectorAll('input[type="checkbox"]:checked');
//   console.log("hi");
//   console.log(markedCheckbox.length == 0)
//   if (markedCheckbox.length == 0) {
//     $('#assignOrders').attr('disabled', 'disabled');
//   }
//   else{
//     $('#assignOrders').removeAttr('disabled');
//   }
// });


// $("input[type='checkbox']").change(function () {
//   console.log("hello");
//   var markedCheckbox = document.querySelectorAll('input[type="checkbox"]:checked');
//   console.log("hi");
//   console.log(markedCheckbox.length == 0)
//   if (markedCheckbox.length == 0) {
//     $('#assignOrders').attr('disabled', 'disabled');
//   }
//   else{
//     $('#assignOrders').removeAttr('disabled');
//   }
//   // var val = $(':checkbox').value;
//   //       console.log(val)
//   //     if (val == '') {
//   //         $('#assignOrders').attr('disabled', 'disabled');
//   //     }else{
//   //         $('#assignOrders').removeAttr('disabled');
//   //     }
// });


// document.getElementById('blankCheckbox').addEventListener('change', function() {
//     console.log('You selected: ', this.value);
//   });