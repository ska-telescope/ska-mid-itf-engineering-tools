// Define the old and new namespaces
// For branch namespaces include 'ci-ska-mid-itf-' in front of the branch name
const oldNamespace = 'ci-ska-mid-itf-at-2226-determine-stable-versions';
const newNamespace = 'staging';

// Define the list of bookmark titles to update
const dishBookmarks = [
    'SKA001',
    'SKA036',
    'SKA063',
    'SKA100'
]
const bookmarksToUpdate = [
    'Telescope',
    'TMC',
    'CSP Monitoring',
    'SDP Integration',
    'CBF Overview',
    'SDP Signal Displays',
    ...dishBookmarks
];

// Function to update bookmarks
function updateBookmarks() {
    bookmarksToUpdate.forEach((bookmarkName) => {
        chrome.bookmarks.search({ title: bookmarkName }, function(results) {
            results.forEach(function(bookmark) {
                if (bookmark.url && (bookmark.url.includes(oldNamespace) || bookmark.url.includes('ci-dish-lmc'))) {
                    let newNamespaceToUse = newNamespace
                    let oldNamespaceToReplace = oldNamespace

                    // Special case for the dishes
                    if (dishBookmarks.includes(bookmarkName)) {
                        // New staging and integration namespaces
                        if (newNamespace === 'staging' || newNamespace === 'integration') {
                            newNamespaceToUse = `${newNamespace}-dish-lmc-${bookmarkName.toLowerCase()}`;
                        }
                        // New on-demand / branch namespaces
                        else if (newNamespace.includes('ci')) {
                            newNamespaceToUse = `ci-dish-lmc-${bookmarkName.toLowerCase()}-${newNamespace.slice(15)}`;
                        }
                        // Replacing staging or integration namespaces
                        if (oldNamespace.includes('staging') || oldNamespace.includes('integration')) {
                            oldNamespaceToReplace = `${oldNamespace}-dish-lmc-${bookmarkName.toLowerCase()}`;
                        }
                        // Replacing on-demand / branch namespaces
                        else if (oldNamespace.includes('ci')) {
                            oldNamespaceToReplace = `ci-dish-lmc-${bookmarkName.toLowerCase()}-${oldNamespace.slice(15)}`;
                        }
                    }

                    // Update the URL
                    chrome.bookmarks.update(bookmark.id, {
                        url: bookmark.url.replace(oldNamespaceToReplace, newNamespaceToUse)
                    }, function(updatedBookmark) {
                        console.log(`Bookmark "${bookmarkName}" updated:`, updatedBookmark);
                    });
                }
            });
        });
    });
}

// Listen for the extension being installed or updated
chrome.runtime.onInstalled.addListener(() => {
    console.log("Bookmark Updater Extension Installed or Updated");
    updateBookmarks();  // Update bookmarks when the extension is installed or updated
});

// Optionally, you could also expose this function to be callable from the popup
chrome.action.onClicked.addListener((tab) => {
    updateBookmarks();
});
