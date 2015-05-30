var showInputKeys = function() {
  var inputKeys = document.getElementById('key');
  var keysObject = JSON.parse(keysRequest.responseText);

  for (var key in keysObject) {
    var option = document.createElement("option");
    option.innerHTML = keysObject[key]['indicatorName'];
//    option.value = keysObject[key]['indicatorName'];
//    option.dataset.value = key;
    inputKeys.appendChild(option);
    window.datasets[keysObject[key]['indicatorName']] = key;
  }
};

window.datasets = {};

var keysRequest = new XMLHttpRequest();
keysRequest.onload = showInputKeys;
keysRequest.open( "GET", 'http://gapminder-api.herokuapp.com/datasets/');
keysRequest.send();

