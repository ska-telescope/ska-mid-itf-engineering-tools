// Define the old and new namespaces
const oldNamespace = 'ci-ska-mid-itf-at-2226-determine-stable-versions';
const newNamespace = 'staging';

// Define the list of bookmark titles to update
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

// Function to update bookmarks
function updateBookmarks() {
    bookmarksToUpdate.forEach((bookmarkName) => {
        chrome.bookmarks.search({ title: bookmarkName }, function(results) {
            results.forEach(function(bookmark) {
                if (bookmark.url && bookmark.url.includes(oldNamespace)) {
                    let newNamespaceToUse = newNamespace

                    // Special case for the dishes and staging
                    if (newNamespace === 'staging' && 
                        (bookmarkName === 'SKA001' || bookmarkName === 'SKA036'))
                    {
                        newNamespaceToUse = `${newNamespace}-dish-lmc-${bookmarkName.toLowerCase()}`;
                    }

                    // Update the URL
                    chrome.bookmarks.update(bookmark.id, {
                        url: bookmark.url.replace(oldNamespace, newNamespaceToUse)
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
