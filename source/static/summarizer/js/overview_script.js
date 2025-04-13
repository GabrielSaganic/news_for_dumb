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
            if (targetElementId === "overview-results") {
                // Populate news results
                targetElement.innerHTML = '';
                if (data === "") {
                    const no_news_title = document.createElement('h1');
                    no_news_title.textContent = "No news found";
                    targetElement.appendChild(no_news_title);
                } else {
                    const paragraph = document.createElement('p');
                    paragraph.textContent = data.content;
                    targetElement.appendChild(paragraph);
                }
            } else if (targetElementId === "categories-results") {
                // Populate checkboxes for tags
                targetElement.innerHTML = '<legend>Choose Categories:</legend>';
                data.forEach(item => {
                    const label = document.createElement('label');
                    label.innerHTML = `<input type="radio" name="categories" value="${item.id}" class="category-checkbox"> ${item.name}`;
                    targetElement.appendChild(label);
                    targetElement.appendChild(document.createElement('br'));
                });

                // Attach event listeners to checkboxes
                const checkboxes = document.querySelectorAll('.category-checkbox');
                checkboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', triggerOverviewEndpoint);
                });
            }
        }

        // Function to trigger the news endpoint
        function triggerOverviewEndpoint() {
            const startDate = document.getElementById("start_date").value;
            const endDate = document.getElementById("end_date").value;
            const selectedCountry = document.querySelector('input[name="country"]:checked')?.value;
            const selectedLength = document.querySelector('input[name="summary-length"]:checked')?.value;
            const selectedCategories = Array.from(document.querySelectorAll('.category-checkbox:checked')).map(cb => cb.value);
            const url = `/summarize_news/news-overview/?country=${selectedCountry}&summary_length=${selectedLength}&start_date=${startDate}&end_date=${endDate}&categories=${selectedCategories.join(",")}`;

            // Fetch data for the news endpoint
            fetchData(url, "overview-results");
        }

        // Function to trigger the tags endpoint
        function triggerCategoriesEndpoint() {
            const startDate = document.getElementById("start_date").value;
            const endDate = document.getElementById("end_date").value;
            const selectedCountry = document.querySelector('input[name="country"]:checked')?.value;
            const categoriesUrl = `/summarize_news/categories/?country=${selectedCountry}&start_date=${startDate}&end_date=${endDate}`;

            // Fetch data for the tags endpoint
            fetchData(categoriesUrl, "categories-results");

        }

        // Add event listeners for date changes
        document.getElementById("start_date").addEventListener("change", () => {
            triggerCategoriesEndpoint();
            triggerOverviewEndpoint();
        });
        document.getElementById("end_date").addEventListener("change", () => {
            triggerCategoriesEndpoint();
            triggerOverviewEndpoint();
        });

        // Add event listeners for country changes
        const countryRadios = document.querySelectorAll('input[name="country"]');
        countryRadios.forEach(radio => {
            radio.addEventListener("change", () => {
                triggerCategoriesEndpoint()
                triggerOverviewEndpoint();
            });
        });

        // Add event listeners for length changes
        const lengthRadios = document.querySelectorAll('input[name="summary-length"]');
        lengthRadios.forEach(radio => {
            radio.addEventListener("change", () => {
                triggerOverviewEndpoint();
            });
        });

        // Trigger the tags and news endpoints on page load
        triggerCategoriesEndpoint();