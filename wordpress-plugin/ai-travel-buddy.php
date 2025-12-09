<?php
/**
 * Plugin Name: AI Travel Buddy - Trip Planner
 * Plugin URI: https://github.com/itsursrujan/ai-travel-buddy
 * Description: Embed an AI-powered trip planner widget in your WordPress site. Users can generate personalized travel itineraries based on destination and budget.
 * Version: 1.0.0
 * Author: AI Travel Buddy Team
 * Author URI: https://aitravel.buddy
 * License: MIT
 * Text Domain: ai-travel-buddy
 * Domain Path: /languages
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('ATB_VERSION', '1.0.0');
define('ATB_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('ATB_PLUGIN_URL', plugin_dir_url(__FILE__));
define('ATB_PLUGIN_BASENAME', plugin_basename(__FILE__));

/**
 * Main plugin class
 */
class AI_Travel_Buddy {
    
    private static $instance = null;
    
    public static function get_instance() {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    private function __construct() {
        $this->init_hooks();
    }
    
    private function init_hooks() {
        // Activation/Deactivation hooks
        register_activation_hook(__FILE__, array($this, 'activate'));
        register_deactivation_hook(__FILE__, array($this, 'deactivate'));
        
        // Admin hooks
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
        
        // Frontend hooks
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_action('wp_footer', array($this, 'add_inline_script'));
        
        // Shortcode
        add_shortcode('ai_travel_planner', array($this, 'render_shortcode'));
        add_shortcode('aitravel', array($this, 'render_shortcode')); // Alias
    }
    
    /**
     * Plugin activation
     */
    public function activate() {
        // Set default options
        $default_options = array(
            'api_url' => 'http://localhost:8000/api',
            'enable_auth' => '0',
            'widget_theme' => 'light',
            'widget_width' => '100%',
            'widget_height' => 'auto'
        );
        
        add_option('atb_settings', $default_options);
    }
    
    /**
     * Plugin deactivation
     */
    public function deactivate() {
        // Clean up if needed
    }
    
    /**
     * Add admin menu
     */
    public function add_admin_menu() {
        add_options_page(
            'AI Travel Buddy Settings',
            'AI Travel Buddy',
            'manage_options',
            'ai-travel-buddy',
            array($this, 'render_admin_page')
        );
    }
    
    /**
     * Register plugin settings
     */
    public function register_settings() {
        register_setting('atb_settings_group', 'atb_settings');
        
        add_settings_section(
            'atb_api_section',
            'API Configuration',
            array($this, 'render_api_section'),
            'ai-travel-buddy'
        );
        
        add_settings_field(
            'api_url',
            'Backend API URL',
            array($this, 'render_api_url_field'),
            'ai-travel-buddy',
            'atb_api_section'
        );
        
        add_settings_field(
            'enable_auth',
            'Enable Authentication',
            array($this, 'render_enable_auth_field'),
            'ai-travel-buddy',
            'atb_api_section'
        );
        
        add_settings_section(
            'atb_widget_section',
            'Widget Appearance',
            array($this, 'render_widget_section'),
            'ai-travel-buddy'
        );
        
        add_settings_field(
            'widget_theme',
            'Widget Theme',
            array($this, 'render_widget_theme_field'),
            'ai-travel-buddy',
            'atb_widget_section'
        );
        
        add_settings_field(
            'widget_width',
            'Widget Width',
            array($this, 'render_widget_width_field'),
            'ai-travel-buddy',
            'atb_widget_section'
        );
    }
    
    /**
     * Render admin page
     */
    public function render_admin_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        
        ?>
        <div class="wrap">
            <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
            <form action="options.php" method="post">
                <?php
                settings_fields('atb_settings_group');
                do_settings_sections('ai-travel-buddy');
                submit_button('Save Settings');
                ?>
            </form>
            
            <div class="atb-usage-section" style="margin-top: 30px; padding: 20px; background: #f5f5f5; border-radius: 5px;">
                <h2>Usage Instructions</h2>
                <h3>Shortcode</h3>
                <p>Add the trip planner widget to any page or post using:</p>
                <code>[ai_travel_planner]</code> or <code>[aitravel]</code>
                
                <h3>With Custom Options</h3>
                <code>[ai_travel_planner theme="dark" width="800px"]</code>
                
                <h3>PHP Code</h3>
                <pre>&lt;?php echo do_shortcode('[ai_travel_planner]'); ?&gt;</pre>
                
                <h3>Gutenberg Block</h3>
                <p>Search for "AI Travel Planner" in the block inserter.</p>
            </div>
        </div>
        <?php
    }
    
    /**
     * Render API section
     */
    public function render_api_section() {
        echo '<p>Configure the backend API endpoint for the trip planner.</p>';
    }
    
    /**
     * Render API URL field
     */
    public function render_api_url_field() {
        $options = get_option('atb_settings');
        $api_url = isset($options['api_url']) ? $options['api_url'] : 'http://localhost:8000/api';
        ?>
        <input type="text" name="atb_settings[api_url]" value="<?php echo esc_attr($api_url); ?>" class="regular-text" />
        <p class="description">Enter your backend API URL (e.g., https://api.aitravel.buddy/api)</p>
        <?php
    }
    
    /**
     * Render enable auth field
     */
    public function render_enable_auth_field() {
        $options = get_option('atb_settings');
        $enable_auth = isset($options['enable_auth']) ? $options['enable_auth'] : '0';
        ?>
        <input type="checkbox" name="atb_settings[enable_auth]" value="1" <?php checked($enable_auth, '1'); ?> />
        <label>Require user authentication to generate itineraries</label>
        <?php
    }
    
    /**
     * Render widget section
     */
    public function render_widget_section() {
        echo '<p>Customize the appearance of the trip planner widget.</p>';
    }
    
    /**
     * Render widget theme field
     */
    public function render_widget_theme_field() {
        $options = get_option('atb_settings');
        $theme = isset($options['widget_theme']) ? $options['widget_theme'] : 'light';
        ?>
        <select name="atb_settings[widget_theme]">
            <option value="light" <?php selected($theme, 'light'); ?>>Light</option>
            <option value="dark" <?php selected($theme, 'dark'); ?>>Dark</option>
            <option value="auto" <?php selected($theme, 'auto'); ?>>Auto (follow site theme)</option>
        </select>
        <?php
    }
    
    /**
     * Render widget width field
     */
    public function render_widget_width_field() {
        $options = get_option('atb_settings');
        $width = isset($options['widget_width']) ? $options['widget_width'] : '100%';
        ?>
        <input type="text" name="atb_settings[widget_width]" value="<?php echo esc_attr($width); ?>" class="small-text" />
        <p class="description">Widget width (e.g., 100%, 800px, 50%)</p>
        <?php
    }
    
    /**
     * Enqueue scripts and styles
     */
    public function enqueue_scripts() {
        // Only load on pages with the shortcode
        global $post;
        if (is_a($post, 'WP_Post') && (has_shortcode($post->post_content, 'ai_travel_planner') || has_shortcode($post->post_content, 'aitravel'))) {
            wp_enqueue_style(
                'atb-widget-style',
                ATB_PLUGIN_URL . 'assets/css/widget.css',
                array(),
                ATB_VERSION
            );
            
            wp_enqueue_script(
                'atb-widget-script',
                ATB_PLUGIN_URL . 'assets/js/widget.js',
                array(),
                ATB_VERSION,
                true
            );
        }
    }
    
    /**
     * Add inline script with configuration
     */
    public function add_inline_script() {
        global $post;
        if (is_a($post, 'WP_Post') && (has_shortcode($post->post_content, 'ai_travel_planner') || has_shortcode($post->post_content, 'aitravel'))) {
            $options = get_option('atb_settings');
            $api_url = isset($options['api_url']) ? $options['api_url'] : 'http://localhost:8000/api';
            $theme = isset($options['widget_theme']) ? $options['widget_theme'] : 'light';
            
            ?>
            <script>
                window.ATBConfig = {
                    apiUrl: '<?php echo esc_js($api_url); ?>',
                    theme: '<?php echo esc_js($theme); ?>'
                };
            </script>
            <?php
        }
    }
    
    /**
     * Render shortcode
     */
    public function render_shortcode($atts) {
        $options = get_option('atb_settings');
        
        // Parse shortcode attributes
        $atts = shortcode_atts(array(
            'theme' => isset($options['widget_theme']) ? $options['widget_theme'] : 'light',
            'width' => isset($options['widget_width']) ? $options['widget_width'] : '100%',
            'height' => 'auto',
            'api_url' => isset($options['api_url']) ? $options['api_url'] : 'http://localhost:8000/api'
        ), $atts, 'ai_travel_planner');
        
        // Ensure scripts are loaded
        wp_enqueue_style('atb-widget-style', ATB_PLUGIN_URL . 'assets/css/widget.css', array(), ATB_VERSION);
        wp_enqueue_script('atb-widget-script', ATB_PLUGIN_URL . 'assets/js/widget.js', array(), ATB_VERSION, true);
        
        // Add inline config
        wp_add_inline_script('atb-widget-script', sprintf(
            'window.ATBConfig = { apiUrl: %s, theme: %s };',
            wp_json_encode($atts['api_url']),
            wp_json_encode($atts['theme'])
        ));
        
        // Generate unique ID for this widget instance
        $widget_id = 'atb-widget-' . uniqid();
        
        ob_start();
        ?>
        <div id="<?php echo esc_attr($widget_id); ?>" 
             class="atb-travel-planner-widget" 
             data-theme="<?php echo esc_attr($atts['theme']); ?>"
             style="width: <?php echo esc_attr($atts['width']); ?>; height: <?php echo esc_attr($atts['height']); ?>;">
            <div class="atb-widget-container">
                <div class="atb-loading">Loading AI Travel Planner...</div>
            </div>
        </div>
        <?php
        return ob_get_clean();
    }
}

// Initialize plugin
function atb_init() {
    return AI_Travel_Buddy::get_instance();
}

// Start the plugin
atb_init();

