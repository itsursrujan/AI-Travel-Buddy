# WordPress Plugin Implementation Guide

## Overview

This guide explains how the WordPress plugin integrates with the AI Travel Buddy backend and how to use it.

## Architecture

```
WordPress Site
    ↓
[Shortcode: [ai_travel_planner]]
    ↓
JavaScript Widget (widget.js)
    ↓
Backend API (Flask)
    ↓
AI Engine (OpenAI)
    ↓
Response → Display in WordPress
```

## Files Created

### 1. `ai-travel-buddy.php` (Main Plugin File)
- Plugin header with metadata
- Settings registration
- Shortcode handler
- Admin menu
- Script/style enqueuing

### 2. `assets/css/widget.css`
- Widget styling
- Theme support (light/dark/auto)
- Responsive design
- Form styling

### 3. `assets/js/widget.js`
- Widget initialization
- Form handling
- API communication
- Itinerary display

### 4. Documentation Files
- `README.md` - User documentation
- `INSTALLATION.md` - Installation steps
- `WORDPRESS_PLUGIN_GUIDE.md` - This file

## Backend Integration

### Public Endpoint Added

A new public endpoint was added to `backend/routes/itinerary_routes.py`:

```python
@itinerary_bp.route("/generate-public", methods=["POST"])
def generate_itinerary_public():
    """Generate itinerary without authentication"""
```

**Key Differences from `/generate`:**
- No JWT token required
- No user authentication
- Does not save to database (optional)
- Perfect for public WordPress widgets

### CORS Configuration

Make sure your WordPress domain is in the backend CORS origins:

```python
# backend/config.py
CORS_ORIGINS = "http://localhost:3000,https://yourwordpresssite.com"
```

## Usage Examples

### Basic Usage
```
[ai_travel_planner]
```

### With Custom Theme
```
[ai_travel_planner theme="dark"]
```

### With Custom Width
```
[ai_travel_planner width="800px"]
```

### Full Customization
```
[ai_travel_planner theme="dark" width="900px" api_url="https://api.example.com/api"]
```

## Customization

### Changing Widget Appearance

Edit `assets/css/widget.css`:

```css
.atb-widget-container {
    /* Your custom styles */
    border-radius: 20px;
    padding: 30px;
}
```

### Modifying Widget Behavior

Edit `assets/js/widget.js`:

```javascript
function handleFormSubmit(form, container, config) {
    // Add custom validation
    // Modify API call
    // Customize response handling
}
```

### Adding Custom Fields

1. Add field to form in `widget.js`
2. Add styling in `widget.css`
3. Include in API request
4. Update backend if needed

## Security Considerations

### Rate Limiting (Recommended)

Add rate limiting to the public endpoint:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@itinerary_bp.route("/generate-public", methods=["POST"])
@limiter.limit("10 per minute")  # Limit to 10 requests per minute per IP
def generate_itinerary_public():
    # ...
```

### Input Validation

The widget validates input on the client side, but backend should also validate:

```python
# Validate destination (no special characters)
# Validate budget (positive number, reasonable range)
# Validate days (1-30)
# Validate travel_style (enum)
```

### API Key Protection

For production, consider:
- API key in WordPress settings
- Backend validates API key
- Per-site rate limiting

## Testing

### Local Testing

1. **Start Backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Test Public Endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/itinerary/generate-public \
     -H "Content-Type: application/json" \
     -d '{"destination":"Paris","budget":5000,"days":7,"travel_style":"leisure"}'
   ```

3. **Install Plugin in WordPress:**
   - Copy to `wp-content/plugins/ai-travel-buddy`
   - Activate in WordPress admin
   - Configure API URL: `http://localhost:8000/api`

4. **Test Widget:**
   - Create a test page
   - Add shortcode: `[ai_travel_planner]`
   - View page and test form

### Production Testing

1. Deploy backend to production
2. Update WordPress plugin settings with production API URL
3. Test widget on staging WordPress site
4. Monitor API logs for errors
5. Test with different themes and configurations

## Troubleshooting

### Widget Not Loading

**Check:**
1. Plugin is activated
2. Scripts/styles are enqueued (view page source)
3. No JavaScript errors (browser console)
4. API URL is correct in settings

### API Errors

**Check:**
1. Backend is running
2. CORS is configured correctly
3. API endpoint exists (`/itinerary/generate-public`)
4. Request format matches expected format

### CORS Issues

**Symptoms:** Browser console shows CORS errors

**Solution:**
1. Add WordPress domain to backend `CORS_ORIGINS`
2. Restart backend server
3. Clear browser cache

### Styling Issues

**Check:**
1. CSS file is loading (view page source)
2. No CSS conflicts with theme
3. Theme attribute is set correctly
4. Custom CSS in theme doesn't override

## Advanced Features

### Optional: Save Public Itineraries

Modify the public endpoint to optionally save:

```python
# Create guest user or use a system user_id
guest_user_id = ObjectId("000000000000000000000000")  # System user

itinerary_doc = Itinerary.create(
    guest_user_id,
    destination,
    budget,
    days,
    travel_style,
    itinerary_data
)
itinerary_doc["is_public"] = True
# Save to database
```

### Optional: Analytics Tracking

Track widget usage:

```python
# Log widget usage
db.widget_usage.insert_one({
    "source": "wordpress",
    "destination": destination,
    "budget": budget,
    "created_at": datetime.utcnow(),
    "ip_address": request.remote_addr
})
```

### Optional: Email Itinerary

Add email functionality to send itinerary:

```python
# After generating itinerary
send_email_with_itinerary(email, itinerary_data)
```

## Deployment Checklist

- [ ] Backend deployed and accessible
- [ ] Public endpoint `/itinerary/generate-public` working
- [ ] CORS configured for WordPress domain
- [ ] Rate limiting implemented
- [ ] Plugin installed in WordPress
- [ ] Settings configured (API URL, theme, etc.)
- [ ] Tested on staging site
- [ ] Widget displays correctly
- [ ] Form submission works
- [ ] Itinerary displays properly
- [ ] Responsive design works
- [ ] No console errors
- [ ] Production ready

## Support

For issues:
1. Check WordPress error logs
2. Check backend logs
3. Review browser console
4. Test API endpoint directly
5. Verify CORS configuration

## Next Steps

1. **Add Rate Limiting** - Protect backend from abuse
2. **Add Analytics** - Track widget usage
3. **Add Caching** - Cache common destinations
4. **Add Email** - Send itinerary via email
5. **Add Social Sharing** - Share itineraries
6. **Add Gutenberg Block** - Native WordPress block

---

**Plugin Version:** 1.0.0  
**Last Updated:** Current  
**Compatible With:** WordPress 5.0+

