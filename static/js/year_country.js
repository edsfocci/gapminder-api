var inputKeys = document.getElementById('input-key');
var resultsTable = document.getElementById('results');
window.currentDataset = "";

var getDatasetOptions = function() {
  if (window.datasets[inputKeys.value] &&
  inputKeys.value != window.currentDataset) {
    clearResultsTable();
    window.currentDataset = inputKeys.value;

    var years = document.getElementById('year');
    var countries = document.getElementById('country');
    years.disabled = true;
    countries.disabled = true;

    var displayOptions = function() {
      var yearCountry = document.getElementById('year-country');

      if (yearCountry.style.display === "inline") {
        while(years.firstChild) {
          years.removeChild(years.firstChild);
        }
        years.appendChild(document.createElement('option'));
        while(countries.firstChild) {
          countries.removeChild(countries.firstChild);
        }
        countries.appendChild(document.createElement('option'));
      }

      var data = JSON.parse(dataRequest.responseText);

      for (var i = 0; i < data.years.data.length; i++) {
        var year = data.years.data[i];
        var option = document.createElement('option');
        option.innerHTML = year;
        years.appendChild(option);
      }

      for (var i = 0; i < data.countries.data.length; i++) {
        var country = data.countries.data[i];
        var option = document.createElement('option');
        option.innerHTML = country;
        countries.appendChild(option);
      }

      years.disabled = false;
      countries.disabled = false;
      yearCountry.style.display = "inline";
    };

    var dataRequest = new XMLHttpRequest();
    dataRequest.onload = displayOptions;
    dataRequest.open( "GET", 'http://gapminder-api.herokuapp.com/data/help/?key=' +
      window.datasets[window.currentDataset]);
    dataRequest.send();
  }
};

var clearResultsTable = function() {
  clearNode(resultsTable);
};

var clearNode = function(element) {
  while(element.firstChild) {
    clearNode(element.firstChild);
    element.removeChild(element.firstChild);
  }
};

setInterval(getDatasetOptions, 100);

