        // Automatically set today's date in the input fields
        const today = new Date().toISOString().split("T")[0];
        document.getElementById("start_date").value = today;
        document.getElementById("end_date").value = today;

        // Function to fetch data from an endpoint
        async function fetchData(url, targetElementId) {
            try {
                const response = await fetch(url);
                if (response.ok) {
                    const data = await response.json();
                    // Render the data into the target element
                    renderData(targetElementId, data);
                } else {
                    console.error(`Error fetching data from ${url}: ${response.statusText}`);
                }
            } catch (error) {
                console.error(`Network error fetching data from ${url}:`, error);
            }
        }

        // Function to render fetched data
        function renderData(targetElementId, data) {
            const targetElement = document.getElementById(targetElementId);

            if (targetElementId === "tags-results") {
                // Populate checkboxes for tags
                targetElement.innerHTML = '<legend>Choose Tags:</legend>';
                data.forEach(item => {
                    const label = document.createElement('label');
                    label.innerHTML = `<input type="checkbox" name="tags" value="${item.id}" class="tag-checkbox"> ${item.name}`;
                    targetElement.appendChild(label);
                    targetElement.appendChild(document.createElement('br'));
                });

                // Attach event listeners to checkboxes
                const checkboxes = document.querySelectorAll('.tag-checkbox');
                checkboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', triggerNewsEndpoint);
                });

            } else if (targetElementId === "news-results") {
                // Populate news results
                targetElement.innerHTML = '';
                if (data.length === 0) {
                    const no_news_title = document.createElement('h1');
                    no_news_title.textContent = "No news found";
                    targetElement.appendChild(no_news_title);
                }
                data.forEach(item => {
                    const title = document.createElement('h3');

                    const link = document.createElement('a');
                    link.textContent = item.title;
                    link.href = item.url;
                    link.target = '_blank';
                    link.style.textDecoration = 'none';
                    link.style.color = 'inherit';

                    title.appendChild(link);

                    const paragraph = document.createElement('p');
                    paragraph.textContent = item.summary_text;
                    targetElement.appendChild(title);
                    targetElement.appendChild(paragraph);
                });
            }
        }

        // Function to trigger the news endpoint
        function triggerNewsEndpoint() {
            const startDate = document.getElementById("start_date").value;
            const endDate = document.getElementById("end_date").value;
            const selectedCountry = document.querySelector('input[name="country"]:checked')?.value;
            const selectedLength = document.querySelector('input[name="summary-length"]:checked')?.value;
            const selectedTags = Array.from(document.querySelectorAll('.tag-checkbox:checked')).map(cb => cb.value);
            const url = `/summarize_news/summarize_news/?country=${selectedCountry}&summary_length=${selectedLength}&start_date=${startDate}&end_date=${endDate}&tags=${selectedTags.join(",")}`;

            // Fetch data for the news endpoint
            fetchData(url, "news-results");
        }

        // Function to trigger the tags endpoint
        function triggerTagsEndpoint() {
            const startDate = document.getElementById("start_date").value;
            const endDate = document.getElementById("end_date").value;
            const selectedCountry = document.querySelector('input[name="country"]:checked')?.value;
            const url = `/summarize_news/tags/?country=${selectedCountry}&start_date=${startDate}&end_date=${endDate}`;

            // Fetch data for the tags endpoint
            fetchData(url, "tags-results");
        }

        // Add event listeners for date changes
        document.getElementById("start_date").addEventListener("change", () => {
            triggerTagsEndpoint();
            triggerNewsEndpoint();
        });
        document.getElementById("end_date").addEventListener("change", () => {
            triggerTagsEndpoint();
            triggerNewsEndpoint();
        });

        // Add event listeners for country changes
        const countryRadios = document.querySelectorAll('input[name="country"]');
        countryRadios.forEach(radio => {
            radio.addEventListener("change", () => {
                triggerTagsEndpoint();
                triggerNewsEndpoint();
            });
        });

        // Add event listeners for country changes
        const lengthRadios = document.querySelectorAll('input[name="summary-length"]');
        lengthRadios.forEach(radio => {
            radio.addEventListener("change", () => {
                triggerNewsEndpoint();
            });
        });

        // Trigger the tags and news endpoints on page load
        triggerTagsEndpoint();
        triggerNewsEndpoint();