const LOCAL_STORAGE_FAVORITES_KEY = "favorites";

// Get stored favorites
function getStoredFavorites() {
	var favorites = JSON.parse(localStorage.getItem(LOCAL_STORAGE_FAVORITES_KEY));
	if (!favorites) {
		favorites = {};
	}
	return favorites;
}

// Add given subreddit to favorites
function addToFavorites(subredditName) {
	// Add to storage
	var favorites = getStoredFavorites();
	favorites[subredditName] = true;
	localStorage.setItem(LOCAL_STORAGE_FAVORITES_KEY, JSON.stringify(favorites));
}

// Remove given subreddit from favorites
function removeFromFavorites(subredditName) {
	var favorites = getStoredFavorites();
	delete favorites[subredditName];
	localStorage.setItem(LOCAL_STORAGE_FAVORITES_KEY, JSON.stringify(favorites));
}

// Check if given subreddit is in favorites
function isFavorite(subredditName) {
	const favoritesState = JSON.parse(
		localStorage.getItem(LOCAL_STORAGE_FAVORITES_KEY),
	);
	if (
		favoritesState &&
		subredditName in favoritesState &&
		favoritesState[subredditName]
	) {
		return true;
	}
	return false;
}

// Change "Add to favorites" / "Remove from favorites" text from button
function toggleFavoriteTextButton(isFavorite) {
	const favoriteElement = document.getElementById(`favorite-link`);
	if (isFavorite) {
		favoriteElement.innerText = "Remove from favorites";
	} else {
		favoriteElement.innerText = "Add to favorites";
	}
}

// biome-ignore lint/correctness/noUnusedVariables: used in template
function onFavoriteButtonClick(subredditName) {
	if (isFavorite(subredditName)) {
		removeFromFavorites(subredditName);
		toggleFavoriteTextButton(false);
	} else {
		addToFavorites(subredditName);
		toggleFavoriteTextButton(true);
	}
	updateFavoritesDropdown();
}

// Update the favorites dropdown menu
function updateFavoritesDropdown() {
	// Fill the dropdown with the local favorites if any
	const favorites = getStoredFavorites();
	const hasFavorites = Object.keys(favorites).length;
	const favoriteDropdown = document.getElementById(`nav-subreddit-dropdown`);
	const favoriteSeparator = document.getElementById(
		`nav-subreddit-dropdown-separator`,
	);

	if (hasFavorites) {
		// Add hr separator to dropdown if not present
		if (favoriteSeparator === null) {
			const separator = document.createElement("hr");
			separator.id = "nav-subreddit-dropdown-separator";
			favoriteDropdown.appendChild(separator);
		}

		// Add dropdown options for subreddit
		for (const [subredditName, _] of Object.entries(favorites)) {
			const newElement = document.createElement("li");
			newElement.className = "nav-subreddit-dropdown-favorite-item";

			const newLink = document.createElement("a");
			newLink.text = "/r/" + subredditName;
			newElement.appendChild(newLink);
			newLink.href = "/r/" + subredditName;
			favoriteDropdown.appendChild(newElement);
		}
	} else {
		// Remove the separator if it is present
		if (favoriteSeparator !== null) {
			favoriteSeparator.remove();
		}

		// Clear favorites
		const favoritesElements = document.getElementsByClassName(
			"nav-subreddit-dropdown-favorite-item",
		);
		for (item of favoritesElements) {
			item.remove();
		}
	}
}

// Init on page load
function initFavorites() {
	// Get favorite link and subreddit name if present (posts lists)
	const favoriteElement = document.getElementById(`favorite-link`);
	if (favoriteElement) {
		const favoriteSubredditName = favoriteElement.dataset.element;
		toggleFavoriteTextButton(isFavorite(favoriteSubredditName));
	}

	updateFavoritesDropdown();
}

// Init
if (document.readyState !== "loading") {
	initFavorites();
} else {
	document.addEventListener("DOMContentLoaded", () => {
		initFavorites();
	});
}
