var years = document.getElementById('year');
var countries = document.getElementById('country');
var resultsTable = document.getElementById('results');

var getOutputs = function() {
  clearResultsTable();
  var year = years.options[years.selectedIndex].text;
  var country = countries.options[countries.selectedIndex].text;

  if (year || country) {
    var displayResults = function() {
      var results = JSON.parse(dataRequest.responseText);

      if (year) {
        var tRow = document.createElement('tr');
        tRow.appendChild(document.createElement('th'));
        var tHeader = document.createElement('th');
        tHeader.innerHTML = results.data.year || results.data[0].year;
        tRow.appendChild(tHeader);
        resultsTable.appendChild(tRow);

        if (results.data.value) {
          tRow = document.createElement('tr');
          tHeader = document.createElement('th');
          tHeader.innerHTML = results.data.country;
          tRow.appendChild(tHeader);

          var tData = document.createElement('td');
          tData.innerHTML = results.data.value;
          tRow.appendChild(tData);
          resultsTable.appendChild(tRow);

        } else {
          for (var i = 0; i < results.data.length; i++) {
            tRow = document.createElement('tr');
            tHeader = document.createElement('th');
            tHeader.style.textAlign = "left";
            tHeader.innerHTML = results.data[i].country;
            tRow.appendChild(tHeader);

            var tData = document.createElement('td');
            tData.innerHTML = results.data[i].value;
            tRow.appendChild(tData);
            resultsTable.appendChild(tRow);
          }
        }
      } else {
        var tRow = document.createElement('tr');
        tRow.appendChild(document.createElement('th'));
        var tHeader = document.createElement('th');
        tHeader.innerHTML = results.data[0].country;
        tRow.appendChild(tHeader);
        resultsTable.appendChild(tRow);

        for (var i = 0; i < results.data.length; i++) {
          tRow = document.createElement('tr');
          tHeader = document.createElement('th');
          tHeader.innerHTML = results.data[i].year;
          tRow.appendChild(tHeader);

          var tData = document.createElement('td');
          tData.innerHTML = results.data[i].value;
          tRow.appendChild(tData);
          resultsTable.appendChild(tRow);
        }
      }
    };

    var dataRequest = new XMLHttpRequest();
    dataRequest.onload = displayResults;
    dataRequest.open( "GET", 'http://localhost:5000/data/?key=' +
      window.datasets[window.currentDataset] +
      '&year=' + year + '&country=' + country);
    dataRequest.send();
  }
};

// Generic helper function
var addEvent = function(element, event, listener, useCapture) {
  var capture = useCapture || false;

  if (element.addEventListener) {
    element.addEventListener(event, listener, useCapture);
  } else if (element.attachEvent) {
    element.attachEvent("on" + event, listener);
  }
};

addEvent(years, 'change', getOutputs);
addEvent(countries, 'change', getOutputs);

var clearResultsTable = function() {
  clearNode(resultsTable);
};

var clearNode = function(element) {
  while(element.firstChild) {
    clearNode(element.firstChild);
    element.removeChild(element.firstChild);
  }
};

