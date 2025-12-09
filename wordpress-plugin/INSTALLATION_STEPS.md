# WordPress Plugin Installation - Step by Step Guide

## Prerequisites

Before installing the plugin, make sure you have:
- ✅ WordPress installation (5.0 or higher)
- ✅ Backend API running (Flask server)
- ✅ Access to WordPress admin panel
- ✅ FTP access or file manager access to WordPress files

---

## Method 1: Manual Installation (Recommended for Development)

### Step 1: Locate Your WordPress Plugins Directory

Your WordPress plugins are located at:
```
/path/to/wordpress/wp-content/plugins/
```

**Common locations:**
- **Local (XAMPP)**: `C:\xampp\htdocs\your-site\wp-content\plugins\`
- **Local (Local by Flywheel)**: `C:\Users\YourName\Local Sites\your-site\app\public\wp-content\plugins\`
- **cPanel**: `/public_html/wp-content/plugins/`
- **Linux Server**: `/var/www/html/wp-content/plugins/`

### Step 2: Copy Plugin Files

**Option A: Using File Manager (cPanel/Server)**
1. Log into your hosting control panel
2. Navigate to File Manager
3. Go to `wp-content/plugins/`
4. Create a new folder named `ai-travel-buddy`
5. Upload all files from `wordpress-plugin/` folder into `ai-travel-buddy/`

**Option B: Using FTP**
1. Connect to your server via FTP (FileZilla, WinSCP, etc.)
2. Navigate to `wp-content/plugins/`
3. Create folder `ai-travel-buddy`
4. Upload all files from `wordpress-plugin/` folder

**Option C: Using Command Line (Linux/Mac)**
```bash
# Navigate to your WordPress plugins directory
cd /path/to/wordpress/wp-content/plugins/

# Copy the plugin folder
cp -r /path/to/AI\ Travel\ Buddy/wordpress-plugin ./ai-travel-buddy
```

**Option D: Using Windows Explorer**
1. Navigate to your WordPress `wp-content/plugins/` folder
2. Create a new folder named `ai-travel-buddy`
3. Copy all files from `wordpress-plugin/` folder
4. Paste them into `ai-travel-buddy` folder

### Step 3: Verify File Structure

Your plugin directory should look like this:
```
wp-content/plugins/ai-travel-buddy/
├── ai-travel-buddy.php
├── assets/
│   ├── css/
│   │   └── widget.css
│   └── js/
│       └── widget.js
├── README.md
├── INSTALLATION.md
└── WORDPRESS_PLUGIN_GUIDE.md
```

### Step 4: Activate the Plugin

1. Log in to your WordPress admin panel
2. Go to **Plugins** → **Installed Plugins**
3. Find **"AI Travel Buddy - Trip Planner"**
4. Click **Activate**

---

## Method 2: ZIP Installation (For Production)

### Step 1: Create ZIP File

**On Windows:**
1. Right-click on `wordpress-plugin` folder
2. Select "Send to" → "Compressed (zipped) folder"
3. Rename to `ai-travel-buddy.zip`

**On Mac/Linux:**
```bash
cd /path/to/AI\ Travel\ Buddy/
zip -r ai-travel-buddy.zip wordpress-plugin/
```

### Step 2: Upload via WordPress Admin

1. Log in to WordPress admin
2. Go to **Plugins** → **Add New**
3. Click **Upload Plugin** button (top of page)
4. Click **Choose File** and select `ai-travel-buddy.zip`
5. Click **Install Now**
6. Click **Activate Plugin** after installation

---

## Method 3: Using WP-CLI (Command Line)

If you have WP-CLI installed:

```bash
# Navigate to WordPress root
cd /path/to/wordpress/

# Install plugin
wp plugin install /path/to/ai-travel-buddy.zip --activate
```

---

## Post-Installation Configuration

### Step 1: Configure Plugin Settings

1. Go to **Settings** → **AI Travel Buddy** in WordPress admin
2. Configure the following:

**Backend API URL:**
- **Local Development**: `http://localhost:8000/api`
- **Production**: `https://your-api-domain.com/api`

**Widget Theme:**
- Choose: Light, Dark, or Auto

**Widget Width:**
- Default: `100%` (or customize like `800px`, `50%`)

3. Click **Save Settings**

### Step 2: Test Backend Connection

Before using the widget, make sure your backend is running:

```bash
# Start backend
cd backend
python main.py
```

Test the API endpoint:
```bash
curl -X POST http://localhost:8000/api/itinerary/generate-public \
  -H "Content-Type: application/json" \
  -d '{"destination":"Paris","budget":5000,"days":7,"travel_style":"leisure"}'
```

### Step 3: Add Widget to a Page

1. Create a new page or edit an existing one
2. Add the shortcode: `[ai_travel_planner]`
3. Publish/Update the page
4. View the page to see the widget

---

## Troubleshooting Installation

### Problem: Plugin Not Appearing in Plugins List

**Solutions:**
1. Check file permissions (folders: 755, files: 644)
2. Verify `ai-travel-buddy.php` is in the correct location
3. Check WordPress error logs: `wp-content/debug.log`
4. Ensure PHP version is 7.4 or higher

### Problem: "Plugin file does not exist" Error

**Solutions:**
1. Verify main plugin file is named exactly `ai-travel-buddy.php`
2. Check that the file is in `wp-content/plugins/ai-travel-buddy/`
3. Ensure file has proper PHP opening tag: `<?php`

### Problem: Plugin Activates But Widget Doesn't Load

**Solutions:**
1. Check browser console (F12) for JavaScript errors
2. Verify API URL in settings is correct
3. Ensure backend is running and accessible
4. Check CORS settings in backend
5. Verify assets folder exists: `assets/css/widget.css` and `assets/js/widget.js`

### Problem: CORS Errors in Browser Console

**Solutions:**
1. Add your WordPress domain to backend CORS:
   ```python
   # backend/config.py
   CORS_ORIGINS = "http://localhost:3000,https://yourwordpresssite.com"
   ```
2. Restart backend server
3. Clear browser cache

### Problem: 404 Error on API Call

**Solutions:**
1. Verify backend is running: `http://localhost:8000/api/health`
2. Check API URL in plugin settings
3. Ensure public endpoint exists: `/api/itinerary/generate-public`
4. Check backend logs for errors

---

## Quick Installation Checklist

- [ ] WordPress installed and accessible
- [ ] Backend API running
- [ ] Plugin files copied to `wp-content/plugins/ai-travel-buddy/`
- [ ] File structure correct (main PHP file in root)
- [ ] Plugin activated in WordPress admin
- [ ] Settings configured (API URL, theme, width)
- [ ] Backend API tested and working
- [ ] CORS configured for WordPress domain
- [ ] Test page created with shortcode
- [ ] Widget displays correctly
- [ ] Form submission works
- [ ] Itinerary generates successfully

---

## Verification Steps

### 1. Check Plugin is Active

Go to **Plugins** → **Installed Plugins** and verify "AI Travel Buddy - Trip Planner" shows as **Active**.

### 2. Check Settings Page

Go to **Settings** → **AI Travel Buddy** and verify you can see the configuration page.

### 3. Check Shortcode Works

1. Create a test page
2. Add: `[ai_travel_planner]`
3. View page
4. You should see the trip planner form

### 4. Test Widget Functionality

1. Fill in the form:
   - Destination: "Paris"
   - Budget: 5000
   - Days: 7
   - Travel Style: Leisure
2. Click "Generate Itinerary"
3. Wait for response
4. Verify itinerary displays

---

## File Permissions (Linux/Unix)

If you're on a Linux server, set proper permissions:

```bash
# Navigate to plugin directory
cd /path/to/wordpress/wp-content/plugins/ai-travel-buddy/

# Set folder permissions
find . -type d -exec chmod 755 {} \;

# Set file permissions
find . -type f -exec chmod 644 {} \;
```

---

## Uninstallation

To remove the plugin:

1. Go to **Plugins** → **Installed Plugins**
2. Find "AI Travel Buddy - Trip Planner"
3. Click **Deactivate**
4. Click **Delete**
5. Confirm deletion

Or manually:
```bash
rm -rf /path/to/wordpress/wp-content/plugins/ai-travel-buddy/
```

---

## Support

If you encounter issues:

1. **Check WordPress Debug Log:**
   - Enable debug mode in `wp-config.php`:
     ```php
     define('WP_DEBUG', true);
     define('WP_DEBUG_LOG', true);
     ```
   - Check `wp-content/debug.log`

2. **Check Browser Console:**
   - Press F12
   - Look for JavaScript errors

3. **Check Backend Logs:**
   - Review Flask server output
   - Check for API errors

4. **Test API Directly:**
   ```bash
   curl -X POST http://localhost:8000/api/itinerary/generate-public \
     -H "Content-Type: application/json" \
     -d '{"destination":"Paris","budget":5000,"days":7,"travel_style":"leisure"}'
   ```

---

## Next Steps After Installation

1. ✅ Configure plugin settings
2. ✅ Test widget on a page
3. ✅ Customize appearance (if needed)
4. ✅ Add to multiple pages/posts
5. ✅ Monitor backend logs
6. ✅ Set up rate limiting (production)
7. ✅ Deploy to production

---

**Installation Complete!** 🎉

Your WordPress plugin is now installed and ready to use. Add `[ai_travel_planner]` to any page or post to display the trip planner widget.

