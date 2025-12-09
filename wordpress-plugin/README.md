# AI Travel Buddy WordPress Plugin

A WordPress plugin that embeds the AI Travel Buddy trip planner widget into your WordPress site. Perfect for travel blogs, NGOs, and tourism websites.

## Features

- ✅ **Easy Embedding**: Use shortcodes to add the trip planner anywhere
- ✅ **Customizable**: Configure API endpoint, theme, and appearance
- ✅ **Responsive Design**: Works on all devices
- ✅ **No Authentication Required**: Public widget (optional auth support)
- ✅ **Theme Support**: Light, dark, and auto themes

## Installation

### Method 1: Manual Installation

1. Download or clone this plugin directory
2. Upload the `wordpress-plugin` folder to `/wp-content/plugins/` directory
3. Rename the folder to `ai-travel-buddy`
4. Activate the plugin through the 'Plugins' menu in WordPress

### Method 2: ZIP Installation

1. Create a ZIP file of the `wordpress-plugin` folder
2. Go to WordPress Admin → Plugins → Add New
3. Click "Upload Plugin"
4. Select the ZIP file and install
5. Activate the plugin

## Configuration

1. Go to **Settings → AI Travel Buddy** in WordPress admin
2. Configure the following:
   - **Backend API URL**: Your backend API endpoint (e.g., `https://api.aitravel.buddy/api`)
   - **Enable Authentication**: Require user login (optional)
   - **Widget Theme**: Light, Dark, or Auto
   - **Widget Width**: Customize widget width

## Usage

### Shortcode

Add the trip planner to any page or post using:

```
[ai_travel_planner]
```

Or use the alias:

```
[aitravel]
```

### With Custom Options

```
[ai_travel_planner theme="dark" width="800px"]
```

### PHP Code

```php
<?php echo do_shortcode('[ai_travel_planner]'); ?>
```

### Gutenberg Block

1. Edit a page/post
2. Click the "+" button to add a block
3. Search for "AI Travel Planner"
4. Insert the block

## Shortcode Parameters

| Parameter | Description | Default | Options |
|-----------|-------------|---------|---------|
| `theme` | Widget theme | `light` | `light`, `dark`, `auto` |
| `width` | Widget width | `100%` | Any CSS width value |
| `height` | Widget height | `auto` | Any CSS height value |
| `api_url` | Override API URL | From settings | Full API URL |

## Backend Requirements

Your backend API must have the following endpoint:

**POST** `/api/itinerary/generate`

**Request Body:**
```json
{
  "destination": "Paris",
  "budget": 5000,
  "days": 7,
  "travel_style": "leisure"
}
```

**Response:**
```json
{
  "message": "Itinerary generated successfully",
  "itinerary": {
    "_id": "...",
    "destination": "Paris",
    "budget": { "amount": 5000, "currency": "USD" },
    "travel_duration": 7,
    "travel_style": "leisure",
    "itinerary": {
      "title": "7 Days in Paris",
      "days": [...],
      "tourist_spots": [...],
      "tips": [...]
    }
  }
}
```

### Public Endpoint (Recommended)

For the WordPress widget to work without authentication, you may want to create a public endpoint in your backend:

```python
# backend/routes/itinerary_routes.py

@itinerary_bp.route("/generate-public", methods=["POST"])
def generate_itinerary_public():
    """Generate itinerary without authentication (for WordPress widget)"""
    # Same logic as /generate but without auth requirement
    # Optionally add rate limiting
    pass
```

## File Structure

```
wordpress-plugin/
├── ai-travel-buddy.php    # Main plugin file
├── assets/
│   ├── css/
│   │   └── widget.css     # Widget styles
│   └── js/
│       └── widget.js      # Widget JavaScript
└── README.md              # This file
```

## Customization

### Styling

Edit `assets/css/widget.css` to customize the widget appearance.

### JavaScript

Edit `assets/js/widget.js` to modify widget behavior.

### PHP

Edit `ai-travel-buddy.php` to add custom functionality.

## Troubleshooting

### Widget Not Loading

1. Check that the plugin is activated
2. Verify the API URL in settings is correct
3. Check browser console for JavaScript errors
4. Ensure your backend API is accessible from the WordPress server

### CORS Issues

If you see CORS errors, add your WordPress domain to the backend CORS configuration:

```python
# backend/config.py
CORS_ORIGINS = "http://localhost:3000,https://yourwordpresssite.com"
```

### API Errors

1. Verify the backend API is running
2. Check API endpoint URL in plugin settings
3. Test the API endpoint directly with curl or Postman

## Development

### Testing Locally

1. Set up a local WordPress installation
2. Install the plugin
3. Configure API URL to point to `http://localhost:8000/api`
4. Test the widget on a page

### Building for Production

1. Ensure all paths use `ATB_PLUGIN_URL` constant
2. Minify CSS and JavaScript (optional)
3. Test on staging WordPress site
4. Create ZIP file for distribution

## Support

For issues or questions:
- GitHub Issues: [Your Repository]
- Email: support@aitravel.buddy

## License

MIT License - Same as main project

## Changelog

### 1.0.0
- Initial release
- Basic widget functionality
- Shortcode support
- Admin settings page
- Theme customization

