// Custom JS to toggle sidebar items
document.addEventListener('DOMContentLoaded', function() {
    const menuHeaders = document.querySelectorAll('.model-section-header');

    menuHeaders.forEach(function(header) {
        header.addEventListener('click', function() {
            const section = header.nextElementSibling;
            if (section.style.display === 'none') {
                section.style.display = 'block';
            } else {
                section.style.display = 'none';
            }
        });
    });
});


//display maps with latitude and longitude

document.addEventListener('DOMContentLoaded', function () {
    // Create a modal element to display the map
    let modal = document.createElement('div');
    modal.style.display = 'none';
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.innerHTML = `
        <div style="position: relative; margin: 10% auto; width: 80%; height: 80%;">
            <div id="map" style="width: 100%; height: 100%;"></div>
            <button id="closeMap" style="position: absolute; top: 10px; right: 10px; z-index: 1000;">Close</button>
        </div>`;
    document.body.appendChild(modal);

    // Handle clicks on the map link
    document.querySelectorAll('.show-map').forEach(function (element) {
        element.addEventListener('click', function (event) {
            event.preventDefault();

            // Get latitude and longitude from the clicked element
            let lat = event.target.getAttribute('data-lat');
            let lng = event.target.getAttribute('data-lng');

            // Display the modal
            modal.style.display = 'block';

            // Initialize the Leaflet map
            let map = L.map('map').setView([lat, lng], 13);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            L.marker([lat, lng]).addTo(map).bindPopup('City Location').openPopup();
        });
    });

    // Close the modal when clicking the close button
    document.getElementById('closeMap').addEventListener('click', function () {
        modal.style.display = 'none';
        modal.innerHTML = ''; // Clear the map to avoid conflicts
    });
});
