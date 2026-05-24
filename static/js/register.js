function myFunction() {
  var x = document.getElementById('psw');
  var y = document.getElementById('psw-repeat');
  if (x.type === 'password') {
    x.type = 'text';
    if (y) y.type = 'text';
  } else {
    x.type = 'password';
    if (y) y.type = 'password';
  }
}

var myInput = document.getElementById('psw');
var letter = document.getElementById('letter');
var capital = document.getElementById('capital');
var number = document.getElementById('number');
var length = document.getElementById('length');

if (myInput) {
  myInput.onfocus = function () {
    document.getElementById('message').style.display = 'block';
  };
  myInput.onblur = function () {
    document.getElementById('message').style.display = 'none';
  };
  myInput.onkeyup = function () {
    var lowerCaseLetters = /[a-z]/g;
    if (myInput.value.match(lowerCaseLetters)) {
      letter.classList.remove('invalid');
      letter.classList.add('valid');
    } else {
      letter.classList.remove('valid');
      letter.classList.add('invalid');
    }
    var upperCaseLetters = /[A-Z]/g;
    if (myInput.value.match(upperCaseLetters)) {
      capital.classList.remove('invalid');
      capital.classList.add('valid');
    } else {
      capital.classList.remove('valid');
      capital.classList.add('invalid');
    }
    var numbers = /[0-9]/g;
    if (myInput.value.match(numbers)) {
      number.classList.remove('invalid');
      number.classList.add('valid');
    } else {
      number.classList.remove('valid');
      number.classList.add('invalid');
    }
    if (myInput.value.length >= 8) {
      length.classList.remove('invalid');
      length.classList.add('valid');
    } else {
      length.classList.remove('valid');
      length.classList.add('invalid');
    }
  };
}

// New Field Validations
document.addEventListener('DOMContentLoaded', function () {
  const fields = [
    { id: 'first_name', min: 2 },
    { id: 'username', min: 2 },
    { id: 'last_name', min: 2 },
    { id: 'email', pattern: /^[a-zA-Z0-9._%+-]+@gmail\.com$/ },
    { id: 'mobile_number', pattern: /^\d{10}$/ },
  ];

  fields.forEach((field) => {
    const input =
      document.getElementsByName(field.id)[0] ||
      document.getElementById(field.id);
    if (input) {
      input.addEventListener('input', function () {
        let isValid = true;
        if (field.min && input.value.length < field.min) isValid = false;
        if (field.pattern && !field.pattern.test(input.value)) isValid = false;

        if (isValid) {
          input.style.borderBottomColor = 'green';
        } else {
          input.style.borderBottomColor = 'red';
        }
      });
    }
  });
});
