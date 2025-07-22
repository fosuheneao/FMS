document.addEventListener('DOMContentLoaded', function() {
    const cropSelect = document.getElementById('id_crop');
    const varietySelect = document.getElementById('id_cropvariety');

    cropSelect.addEventListener('change', function () {
        const cropId = this.value;

        // Clear previous options
        varietySelect.length = 0;

        if (!cropId) return;

        fetch(`/yuapp/ajax/load-crop-varieties/?crop=${cropId}`)
            .then(response => response.json())
            .then(data => {
                const emptyOption = document.createElement('option');
                emptyOption.value = '';
                emptyOption.textContent = '---------';
                varietySelect.appendChild(emptyOption);

                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.textContent = item.name;
                    varietySelect.appendChild(option);
                });
            });
    });
});
