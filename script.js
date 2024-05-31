function populateSelect(apiEndpoint, selectElementId) {
  fetch(apiEndpoint)
    .then((response) => response.json())
    .then((data) => {
      let selectElement = document.getElementById(selectElementId);
      data.forEach((option) => {
        let optionElement = document.createElement("option");
        optionElement.textContent = option;
        selectElement.appendChild(optionElement);
      });
    })
    .catch((error) => console.error("Error fetching data:", error));
}

populateSelect("http://127.0.0.1:5000/brands", "brand");

populateSelect("http://127.0.0.1:5000/models", "models");

populateSelect("http://127.0.0.1:5000/series", "bodyType");

populateSelect("http://127.0.0.1:5000/transmissions", "transmission");

populateSelect("http://127.0.0.1:5000/engine_types", "fuelType");

document.getElementById("carForm").addEventListener("submit", function (event) {
  event.preventDefault();

  let year = parseInt(document.getElementById("year").value);
  let origin = document.getElementById("origin").value;
  let bodyType = document.getElementById("bodyType").value;
  let kilometers = parseFloat(document.getElementById("kilometers").value);
  let fuelType = document.getElementById("fuelType").value;
  let transmission = document.getElementById("transmission").value;
  let brand = document.getElementById("brand").value;
  let model = document.getElementById("models").value;

  let formData = {
    year: year,
    assemble_place: origin,
    series: bodyType,
    km: kilometers,
    engine_type: fuelType,
    transmission: transmission,
    brand: brand,
    model: model,
  };

  fetch("http://127.0.0.1:5000/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.json())
    .then((data) => {
      let price = data["price"];
      let low_price = data["low_price"];
      let high_price = data["high_price"];
      document.getElementById("price").textContent = "Giá thấp nhất: " + low_price + " - Giá dự đoán: " + price + " - Giá cao nhất: " + high_price;
    })
    .catch((error) => {
      console.error("Error sending data:", error);
    });
});
