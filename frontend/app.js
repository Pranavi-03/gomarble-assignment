

// Function to fetch reviews from the API
const fetchReviews = async () => {
    const urlInput = document.getElementById("urlInput").value; // Get the input URL
    const outputDiv = document.getElementById("output"); // Div to display reviews

    if (!urlInput) {
        outputDiv.innerHTML = "<p style='color: red;'>Please enter a valid URL!</p>";
        return;
    }

    try {
        // Send a GET request to the backend API with the product URL
        const response = await fetch(`https://gomarble-api.onrender.com/api/reviews?url=${encodeURIComponent(urlInput)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        // Display the reviews if found
        if (data.reviews) {
            outputDiv.innerHTML = `
                <h2>Reviews (${data.reviews_count})</h2>
                <ul>
                    ${data.reviews.map(review => `
                        <li>
                            <strong>${review.title || "No Title"}</strong><br>
                            ${review.body || "No Body"}<br>
                            <em>Rating: ${review.rating || "N/A"} - By ${review.reviewer || "Anonymous"}</em>
                        </li>
                    `).join('')}
                </ul>
            `;
        } else {
            outputDiv.innerHTML = "<p>No reviews found for the given URL.</p>";
        }
    } catch (error) {
        outputDiv.innerHTML = `<p style='color: red;'>Error fetching reviews: ${error.message}</p>`;
    }
};

// Attach the fetchReviews function to the button click event
document.getElementById("fetchReviews").addEventListener("click", fetchReviews);
