const LOCAL_STORAGE_FAVORITES_KEY = "favorites";

// Add given subreddit to favorites
function addToFavorites(subredditName) {
    // Add to storage
    var favorites = JSON.parse(localStorage.getItem(LOCAL_STORAGE_FAVORITES_KEY));
    if (!favorites) {
        favorites = {}
    }
    favorites[subredditName] = true
    localStorage.setItem(LOCAL_STORAGE_FAVORITES_KEY, JSON.stringify(favorites))
}

// Remove given subreddit from favorites
function removeFromFavorites(subredditName) {
    // Add to storage
    var favorites = JSON.parse(localStorage.getItem(LOCAL_STORAGE_FAVORITES_KEY));
    delete favorites[subredditName]
    localStorage.setItem(LOCAL_STORAGE_FAVORITES_KEY, JSON.stringify(favorites))
}

// Check if given subreddit is in favorites
function isFavorite(subredditName) {
    const favoritesState = JSON.parse(localStorage.getItem(LOCAL_STORAGE_FAVORITES_KEY));
    if (favoritesState && subredditName in favoritesState && favoritesState[subredditName]) {
        return true;
    }
    return false;
}

// Change "Add to favorites" / "Remove from favorites" text from button
function toggleFavoriteTextButton(subredditName, isFavorite) {
    const favoriteElement = document.getElementById(`favorite-link`);
    if (isFavorite) {
        favoriteElement.innerText = "Remove from favorites"
    } else {
        favoriteElement.innerText = "Add to favorites"
    }
}

function onFavoriteButtonClick(subredditName) {
    if (isFavorite(subredditName)) {
        removeFromFavorites(subredditName)
        toggleFavoriteTextButton(subredditName, false)
    } else {
        addToFavorites(subredditName)
        toggleFavoriteTextButton(subredditName, true)
    }
}

// Init on page load
function initFavorites() {
    // Get favorite link and subreddit name if present (posts lists)
    const favoriteElement = document.getElementById(`favorite-link`);
    if (favoriteElement) {
        const favoriteSubredditName = favoriteElement.dataset["element"];
    }


}

// Init
if (document.readyState !== "loading") {
	initFavorites();
} else {
	document.addEventListener("DOMContentLoaded", () => {
		initFavorites();
	});
}
