(function($){
  $(function(){
    $('.sidenav').sidenav();
    $('select').formSelect();
    $('.tabs').tabs();

    $('#submit').on('click', () => {
      var call = $('#formcountries').serialize()

      $.ajax({
        type: "POST",
        url: '/data/compute/alldata/',
        data: call,
        success: (ret) => handleContents(ret),
        dataType: 'text'
      })

    })
  })
  // getCountryList()
  makeMap()
})(jQuery)


function getCountryList() {
  $.get("/data/fetch/countries", function( data ) {
    data = JSON.parse(data)

    console.log(data)
    
    var countriesdiv = document.getElementById('countries')
    var html = ""
    
    Object.keys(data).forEach(function(key) {
      html += `<div class="col s6 m3"><label><input type="checkbox" id="${data[key]}" name="${data[key]}"/><span>${data[key]}</span></label></div>`
    })
    countriesdiv.innerHTML = html
  })
}


function handleContents(ct) {

  clearContents()

  data = JSON.parse(ct)

  console.log(data)

  var mainContainer = document.getElementById('mainContent')

  var collapsible = document.createElement('ul')
  collapsible.className = 'collapsible'

  mainContainer.appendChild(collapsible)

  Object.keys(data).forEach((type) => {
    var caseType = data[type]

    var collapsibleLi = document.createElement('li')

    collapsible.appendChild(collapsibleLi)

    var collapsibleHeader = document.createElement('div')
    collapsibleHeader.className = 'collapsible-header'
    collapsibleHeader.innerHTML = `${capitalizeFirstLetter(type)}`

    var collapsibleBody = document.createElement('div')
    collapsibleBody.className = 'collapsible-body'

    collapsibleLi.appendChild(collapsibleHeader)
    collapsibleLi.appendChild(collapsibleBody)

    Object.keys(caseType).forEach((measure) => {
      var measureType = caseType[measure]

      Object.keys(measureType).forEach((processed) => {
        var processedType = measureType[processed]
        var values = []        

        Object.keys(processedType).forEach((country) => {
          var countryType = processedType[country]
          values.push({
            x: Object.keys(countryType).map(cleanDate),
            y: Object.values(countryType),
            type: 'scatter',
            name: country
          })
        })
        createGraphLog(capitalizeFirstLetter(`${type} ${measure} ${processed}`), values, collapsibleBody)
      })
    })
  })
  var elems = document.querySelectorAll('.collapsible');
  M.Collapsible.init(elems, {
    onOpenEnd: triggerResize
  })
}

function cleanDate(x) {
  var d = new Date(x * 1000)
  d.setHours(0, 0, 0, 0)
  return d
}

function createGraphLog(name, data, parent) {
  var layout = {
    title: name,
    xaxis: {
      title: 'Date',
      showgrid: true,
      zeroline: true
    },
    yaxis: {
      title: '',
      showline: false
    },
  };

  // Plott
  var newplotdiv = document.createElement('div')
  newplotdiv.id = name; 
  newplotdiv.classList.add("control-panel")

  // Summing all
  parent.appendChild(newplotdiv);

  Plotly.newPlot(name, data, layout, {responsive: true});
}


function updateGraphLog(name, values) {
  Plotly.newPlot(name,
    [{x: ALL_MESSAGES.Timestamp, 
      y: values, 
      type: 'scatter'}], 
    layout = {
    title: name,
    xaxis: {
      title: 'Time',
      showgrid: true,
      zeroline: true
    },
    yaxis: {
      title: '',
      showline: false
    },
  } , {responsive: true});
}


function updateValueWithFilter(name) {
  if (ALL_MESSAGES[name].filter.active) {
    ALL_MESSAGES[name].filter.values = filterData(ALL_MESSAGES[name].values, ALL_MESSAGES[name].filter.r, ALL_MESSAGES[name].filter.q)
    updateGraphLog(name, ALL_MESSAGES[name].filter.values);
  } else {
    updateGraphLog(name, ALL_MESSAGES[name].values);
  }
}

function filterData(data, R, Q) {
  if (R == 0 && Q == 0) {
    return data;
  } 
  var kalmanFilter = new KalmanFilter({R: R, Q: Q});
  var dataConstantKalman = data.map(function(v) {
    return kalmanFilter.filter(v);
  });
  return dataConstantKalman;
}

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

function clearContents() {
  document.getElementById('mainContent').innerHTML = "";
}

function triggerResize () {
  // workaround
  window.dispatchEvent(new Event('resize'))
}


function makeMap() {
  var mainmap = L.map('mapcontainer', {
    scrollWheelZoom: false,
    center: [51.505, -0.09],
    zoom: 3
  })
  var Stadia_AlidadeSmoothDark = L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', {
    maxZoom: 20,
    attribution: '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors'
  })
  Stadia_AlidadeSmoothDark.addTo(mainmap)

  fetch('/static/res/archive/countries.geojson')
  .then((response) => {
    return response.json()
  }).then((countryBorders) => {
    console.log(countryBorders)
    L.geoJSON(countryBorders, {
      onEachFeature: onEachFeature
    }).addTo(mainmap)
  })
}

function onEachFeature(feature, layer) {

  // add popup layer
  layer.bindPopup('<p class="white-text">Loading...</p>');

  //bind click
  layer.on({
    click: (e) => {
      var popup = e.target.getPopup()
      let name = e.sourceTarget.feature.properties.ISO_A3 // ISO_A3
      $.ajax({
        type: "POST",
        url: '/data/compute/lockdown/',
        data: {
          country: name
        },
        success: (ret) => {
          var result = JSON.parse(ret)
          var valuesLength = Object.values(Object.values(result.confirmed.Cumulative.Raw)[0]).length
          var endIndex = Object.values(result.lockdown.Gauss.Derivative.prediction).findIndex(x => x < 1)
          if (endIndex >= 0) {
            var endDate = Object.keys(result.lockdown.Gauss.Derivative.prediction)[endIndex]
          } else {
            var endDate = 'No data'
          }

          popup.setContent(`
          <div class="center">
          <h5 class="white-text">${e.sourceTarget.feature.properties.ADMIN}</h5>
          <div style="border: solid orange;">
            <h6 class="orange-text">Expected end of lockdown</h6>
            <h4 class="orange-text">${new Date(endDate * 1000).toDateString()}</h4>
          </div>
          <table class="centered">
          <thead>
            <tr>
              <th class="blue-text">Confirmed</th>
              <th class="red-text">Deaths</th>
              <th class="green-text">Recovered</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><h5 class="white-text">${Object.values(Object.values(result.confirmed.Cumulative.Raw)[0])[valuesLength - 1]}</h5></td>
              <td><h5 class="white-text">${Object.values(Object.values(result.deaths.Cumulative.Raw)[0])[valuesLength - 1]}</h5></td>
              <td><h5 class="white-text">${Object.values(Object.values(result.recovered.Cumulative.Raw)[0])[valuesLength - 1]}</h5></td>
            </tr>
          </tbody>
          </table>
          </div>`)
          popup.update()

          console.log(result.lockdown.Gauss.Derivative)

          var values = []
          Object.entries(result.lockdown.Gauss.Derivative).forEach(([key, value]) => {
            var country = value
            values.push({
              x: Object.keys(country).map(cleanDate),
              y: Object.values(country),
              type: 'scatter',
              name: name
            })
          })
          console.log(values)

          var collapsibleBody = document.getElementById('countries')
          createGraphLog(capitalizeFirstLetter('Expected curve'), values, collapsibleBody)
        },
        dataType: 'text'
      })
    }
  })

  layer.on('mouseover', (e) => {
    let name = e.sourceTarget.feature.properties.ISO_A3 // ISO_A3
    layer.setStyle({color: '#ff0000'})
  })

  layer.on('mouseout', (e) => {
    layer.setStyle({color: '#3388ff'})
  })

}
