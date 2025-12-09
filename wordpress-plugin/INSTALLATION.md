# WordPress Plugin Installation Guide

## Quick Start

### Step 1: Copy Plugin Files

Copy the `wordpress-plugin` folder to your WordPress plugins directory:

**On Linux/Mac:**
```bash
cp -r wordpress-plugin /path/to/wordpress/wp-content/plugins/ai-travel-buddy
```

**On Windows:**
```powershell
xcopy wordpress-plugin "C:\path\to\wordpress\wp-content\plugins\ai-travel-buddy" /E /I
```

Or manually:
1. Navigate to your WordPress installation
2. Go to `wp-content/plugins/`
3. Create folder `ai-travel-buddy`
4. Copy all files from `wordpress-plugin/` into it

### Step 2: Activate Plugin

1. Log in to WordPress Admin
2. Go to **Plugins** → **Installed Plugins**
3. Find "AI Travel Buddy - Trip Planner"
4. Click **Activate**

### Step 3: Configure Settings

1. Go to **Settings** → **AI Travel Buddy**
2. Enter your backend API URL:
   - Local: `http://localhost:8000/api`
   - Production: `https://api.aitravel.buddy/api`
3. Choose widget theme (Light/Dark/Auto)
4. Set widget width
5. Click **Save Settings**

### Step 4: Add Widget to Page

1. Edit any page or post
2. Add shortcode: `[ai_travel_planner]`
3. Publish/Update the page
4. View the page to see the widget

## Backend Setup

### Option 1: Use Existing Endpoint (Requires Auth)

If your backend requires authentication, you'll need to create a public endpoint.

### Option 2: Create Public Endpoint (Recommended)

Add this to your backend:

```python
# backend/routes/itinerary_routes.py

@itinerary_bp.route("/generate-public", methods=["POST"])
def generate_itinerary_public():
    """Generate itinerary without authentication (for WordPress widget)"""
    try:
        data = request.get_json()
        destination = data.get("destination")
        budget = data.get("budget")
        days = data.get("days", 3)
        travel_style = data.get("travel_style", "leisure")

        if not all([destination, budget]):
            return jsonify({"error": "Destination and budget required"}), 400

        # Generate itinerary using AI engine
        ai_engine = AIEngine()
        from config import Config
        if Config.OPENAI_API_KEY:
            itinerary_data = ai_engine.generate_itinerary(destination, budget, days, travel_style)
        else:
            itinerary_data = ai_engine.get_sample_itinerary(destination, budget, days, travel_style)

        # Return itinerary without saving to database (or save with guest user)
        return jsonify({
            "message": "Itinerary generated successfully",
            "itinerary": {
                "destination": destination,
                "budget": {"amount": budget, "currency": "USD"},
                "travel_duration": days,
                "travel_style": travel_style,
                "itinerary": itinerary_data
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

Then update the WordPress plugin JavaScript to use `/itinerary/generate-public` instead of `/itinerary/generate`.

### Update CORS Settings

Add your WordPress domain to backend CORS:

```python
# backend/config.py
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://yourwordpresssite.com").split(",")
```

## Testing

### Test Widget Locally

1. Start your backend: `cd backend && python main.py`
2. Start WordPress (XAMPP, Local by Flywheel, etc.)
3. Create a test page with `[ai_travel_planner]`
4. Visit the page and test the widget

### Test API Connection

```bash
curl -X POST http://localhost:8000/api/itinerary/generate-public \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris",
    "budget": 5000,
    "days": 7,
    "travel_style": "leisure"
  }'
```

## Troubleshooting

### Plugin Not Appearing

- Check file permissions (should be readable)
- Verify plugin folder name is `ai-travel-buddy`
- Check WordPress error logs

### Widget Not Loading

- Open browser console (F12)
- Check for JavaScript errors
- Verify API URL in settings
- Test API endpoint directly

### CORS Errors

- Add WordPress domain to backend CORS_ORIGINS
- Restart backend server
- Clear browser cache

### API Connection Failed

- Verify backend is running
- Check API URL in plugin settings
- Test API with curl/Postman
- Check firewall/network settings

## Production Deployment

1. **Update API URL** to production endpoint
2. **Test thoroughly** on staging site
3. **Minify assets** (optional):
   ```bash
   # Minify CSS
   npx cssnano assets/css/widget.css assets/css/widget.min.css
   
   # Minify JS
   npx terser assets/js/widget.js -o assets/js/widget.min.js
   ```
4. **Update file references** in PHP to use `.min` versions
5. **Deploy** to production WordPress site

## Support

For installation help:
- Check WordPress error logs
- Enable WordPress debug mode
- Review browser console errors
- Test API endpoint independently

