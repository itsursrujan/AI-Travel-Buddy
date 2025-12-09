/**
 * AI Travel Buddy Widget JavaScript
 * Embeds the trip planner widget in WordPress
 */

(function() {
    'use strict';
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWidget);
    } else {
        initWidget();
    }
    
    function initWidget() {
        const widgets = document.querySelectorAll('.atb-travel-planner-widget');
        
        widgets.forEach(function(widget) {
            const container = widget.querySelector('.atb-widget-container');
            if (container) {
                renderWidget(container, widget);
            }
        });
    }
    
    function renderWidget(container, widgetElement) {
        const config = window.ATBConfig || {
            apiUrl: 'http://localhost:8000/api',
            theme: 'light'
        };
        
        const theme = widgetElement.getAttribute('data-theme') || config.theme || 'light';
        
        // Render the form
        container.innerHTML = `
            <div class="atb-form-container">
                <h2 class="atb-widget-title">Plan Your Perfect Trip with AI</h2>
                <p class="atb-widget-subtitle">Enter your destination, budget, and travel style to generate a personalized itinerary.</p>
                
                <form class="atb-form" id="atb-planner-form">
                    <div class="atb-error" id="atb-error" style="display: none;"></div>
                    <div class="atb-success" id="atb-success" style="display: none;"></div>
                    
                    <div class="atb-form-grid">
                        <div class="atb-form-group">
                            <label for="atb-destination">Destination *</label>
                            <input 
                                type="text" 
                                id="atb-destination" 
                                name="destination" 
                                placeholder="e.g., Paris, Tokyo, Barcelona" 
                                required
                            />
                        </div>
                        
                        <div class="atb-form-group">
                            <label for="atb-budget">Budget (USD) *</label>
                            <input 
                                type="number" 
                                id="atb-budget" 
                                name="budget" 
                                placeholder="e.g., 5000" 
                                min="1"
                                required
                            />
                        </div>
                        
                        <div class="atb-form-group">
                            <label for="atb-days">Duration (Days) *</label>
                            <input 
                                type="number" 
                                id="atb-days" 
                                name="days" 
                                placeholder="e.g., 7" 
                                min="1"
                                max="30"
                                required
                            />
                        </div>
                        
                        <div class="atb-form-group">
                            <label for="atb-travel-style">Travel Style *</label>
                            <select id="atb-travel-style" name="travel_style" required>
                                <option value="leisure">Leisure</option>
                                <option value="adventure">Adventure</option>
                                <option value="cultural">Cultural</option>
                                <option value="budget">Budget</option>
                            </select>
                        </div>
                    </div>
                    
                    <button type="submit" class="atb-button" id="atb-submit-btn">
                        Generate Itinerary
                    </button>
                </form>
                
                <div id="atb-results" style="display: none;"></div>
            </div>
        `;
        
        // Attach form handler
        const form = container.querySelector('#atb-planner-form');
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                handleFormSubmit(form, container, config);
            });
        }
    }
    
    function handleFormSubmit(form, container, config) {
        const errorDiv = container.querySelector('#atb-error');
        const successDiv = container.querySelector('#atb-success');
        const submitBtn = container.querySelector('#atb-submit-btn');
        const resultsDiv = container.querySelector('#atb-results');
        
        // Hide previous messages
        if (errorDiv) errorDiv.style.display = 'none';
        if (successDiv) successDiv.style.display = 'none';
        if (resultsDiv) resultsDiv.style.display = 'none';
        
        // Get form data
        const formData = new FormData(form);
        const destination = formData.get('destination');
        const budget = parseFloat(formData.get('budget'));
        const days = parseInt(formData.get('days'));
        const travelStyle = formData.get('travel_style');
        
        // Validate
        if (!destination || !budget || !days || !travelStyle) {
            showError(errorDiv, 'Please fill in all required fields.');
            return;
        }
        
        // Disable submit button
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Generating Itinerary...';
        }
        
        // Make API call to public endpoint (no authentication required)
        fetch(config.apiUrl + '/itinerary/generate-public', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                destination: destination,
                budget: budget,
                days: days,
                travel_style: travelStyle
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'Failed to generate itinerary');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.itinerary) {
                displayItinerary(resultsDiv, data.itinerary, config);
                if (successDiv) {
                    successDiv.textContent = 'Itinerary generated successfully!';
                    successDiv.style.display = 'block';
                }
            } else {
                throw new Error('Invalid response from server');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError(errorDiv, error.message || 'Failed to generate itinerary. Please try again.');
        })
        .finally(() => {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Generate Itinerary';
            }
        });
    }
    
    function showError(errorDiv, message) {
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }
    
    function displayItinerary(resultsDiv, itinerary, config) {
        if (!resultsDiv) return;
        
        const itineraryData = itinerary.itinerary || {};
        const days = itineraryData.days || [];
        const touristSpots = itineraryData.tourist_spots || [];
        const tips = itineraryData.tips || [];
        
        let html = `
            <div class="atb-itinerary">
                <h3 class="atb-itinerary-title">${itinerary.destination} - ${itinerary.travel_duration} Days</h3>
                <div class="atb-itinerary-meta">
                    <p><strong>Budget:</strong> $${itinerary.budget.amount} ${itinerary.budget.currency}</p>
                    <p><strong>Travel Style:</strong> ${itinerary.travel_style}</p>
                </div>
        `;
        
        // Display days
        if (days.length > 0) {
            html += '<div class="atb-days-container">';
            days.forEach(function(day) {
                html += `
                    <div class="atb-day-section">
                        <h4 class="atb-day-title">${day.title || 'Day ' + day.day}</h4>
                        ${day.total_cost ? `<p class="atb-day-cost"><strong>Estimated Cost:</strong> ${day.total_cost}</p>` : ''}
                `;
                
                // Activities
                if (day.activities && day.activities.length > 0) {
                    html += '<div class="atb-activities">';
                    day.activities.forEach(function(activity) {
                        html += `
                            <div class="atb-activity">
                                <span class="atb-activity-time">${activity.time || ''}</span>
                                <span class="atb-activity-name">${activity.activity || ''}</span>
                                ${activity.cost ? `<span class="atb-activity-cost">${activity.cost}</span>` : ''}
                            </div>
                        `;
                    });
                    html += '</div>';
                }
                
                // Meals
                if (day.meals) {
                    html += `
                        <div class="atb-meals">
                            <p><strong>Meals:</strong></p>
                            <ul>
                                ${day.meals.breakfast ? `<li>Breakfast: ${day.meals.breakfast}</li>` : ''}
                                ${day.meals.lunch ? `<li>Lunch: ${day.meals.lunch}</li>` : ''}
                                ${day.meals.dinner ? `<li>Dinner: ${day.meals.dinner}</li>` : ''}
                            </ul>
                        </div>
                    `;
                }
                
                html += '</div>';
            });
            html += '</div>';
        }
        
        // Tourist spots
        if (touristSpots.length > 0) {
            html += '<div class="atb-tourist-spots"><h4>Must-Visit Tourist Spots</h4><ul>';
            touristSpots.forEach(function(spot) {
                html += `
                    <li>
                        <strong>${spot.name}</strong> - ${spot.description || ''}
                        ${spot.ticket_price ? ` (${spot.ticket_price})` : ''}
                    </li>
                `;
            });
            html += '</ul></div>';
        }
        
        // Tips
        if (tips.length > 0) {
            html += '<div class="atb-tips"><h4>Travel Tips</h4><ul>';
            tips.forEach(function(tip) {
                html += `<li>${tip}</li>`;
            });
            html += '</ul></div>';
        }
        
        html += '</div>';
        
        resultsDiv.innerHTML = html;
        resultsDiv.style.display = 'block';
        
        // Scroll to results
        resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
})();

