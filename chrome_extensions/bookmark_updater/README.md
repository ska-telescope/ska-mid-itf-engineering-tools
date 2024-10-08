# Bookmark Updater Chrome Extension

## Overview
The Bookmark Updater is a Chrome extension designed to automatically update specified bookmarks' URLs to new namespaces. It is meant to be used in Alfred's profile, as the default bookmarks are from there, but can be adjusted to work on any bookmarks and be added to any profile. It operates in the background, ensuring that the bookmarks are updated whenever the extension is installed or updated.

## Installation
To install the extension locally:
1. Clone the repository or download the files to your local machine.
2. Open Chrome and navigate to `chrome://extensions/`.
3. Enable "Developer mode" by toggling the switch in the upper right corner.
4. Click "Load unpacked" and select the `bookmark_updater` project from the `chrome_extensions` directory.
5. The extension should now be visible in the Chrome extension manager.

## Configuration
The extension uses the following configuration:
- **Old Namespace**: The part of the URL to be replaced.
- **New Namespace**: The new part of the URL that replaces the old namespace.
- **Bookmarks to Update**: A list of bookmark titles that the extension will search for and update.

### Default Configuration (in `background.js`)

```javascript
const oldNamespace = 'ci-ska-mid-itf-at-2226-determine-stable-versions';
const newNamespace = 'staging';

const bookmarksToUpdate = [
    'Telescope',
    'TMC',
    'CSP Monitoring',
    'SDP Integration', 
    'CBF Overview',
    'SDP Signal Displays',
    'SKA001',
    'SKA036'
];
```
Note: the last two are in the `Dishes` folder in the bookmarks bar. However, child bookmarks are specified directly and should not include the parent folder name.

## Usage
- Once installed, the extension runs automatically in the background.
- It checks the specified bookmarks and updates their URLs based on the configured namespaces.
- It will skip any URLs that do not contain the old namespace.
- No user interaction is required after the initial setup.

## Modifying the Extension
To modify the list of bookmarks or the namespace:
1. Open `background.js` in the `bookmark_updater` directory.
2. Edit the `oldNamespace`, `newNamespace`, and `bookmarksToUpdate` variables as needed.
3. Save your changes.
4. Reload the extension in Chrome by going to `chrome://extensions/` and clicking the "Reload" button under the Bookmark Updater extension.

    ![alt text](reload_and_enable_toggle.png)

## Additional Notes
- The extension logs updates to the Chrome DevTools console, accessible via `chrome://extensions/` > "Inspect views" under the Bookmark Updater extension details.
- If you encounter issues, try reloading the extension from the Chrome Extensions page.
- The extension requires only access to bookmarks, ensuring it operates securely and efficiently.

