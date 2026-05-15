const LOCAL_STORAGE_FAVORITES_KEY = "favorites";
const FAVORITE_LINK_ID = "favorite-link";
const DROPDOWN_ID = "nav-subreddit-dropdown";
const SEPARATOR_ID = "nav-subreddit-dropdown-separator";
const FAVORITE_ITEM_CLASS = "nav-subreddit-dropdown-favorite-item";

// Get stored favorites as an array. Legacy object-shaped data is discarded.
function getStoredFavorites() {
	const stored = JSON.parse(localStorage.getItem(LOCAL_STORAGE_FAVORITES_KEY));
	return Array.isArray(stored) ? stored : [];
}

function saveFavorites(favorites) {
	localStorage.setItem(LOCAL_STORAGE_FAVORITES_KEY, JSON.stringify(favorites));
}

function addToFavorites(subredditName) {
	const favorites = getStoredFavorites();
	if (!favorites.includes(subredditName)) {
		favorites.push(subredditName);
		saveFavorites(favorites);
	}
}

function removeFromFavorites(subredditName) {
	saveFavorites(getStoredFavorites().filter((name) => name !== subredditName));
}

function isFavorite(subredditName) {
	return getStoredFavorites().includes(subredditName);
}

function toggleFavoriteTextButton(isFav) {
	const favoriteElement = document.getElementById(FAVORITE_LINK_ID);
	favoriteElement.innerText = isFav
		? "Remove from favorites"
		: "Add to favorites";
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

function updateFavoritesDropdown() {
	const dropdown = document.getElementById(DROPDOWN_ID);

	// Clear any existing favorite items and separator so the rebuild is idempotent.
	const existingItems = Array.from(
		document.getElementsByClassName(FAVORITE_ITEM_CLASS),
	);
	for (const item of existingItems) {
		item.remove();
	}
	const existingSeparator = document.getElementById(SEPARATOR_ID);
	if (existingSeparator) {
		existingSeparator.remove();
	}

	// Get stored favorites
	const favorites = getStoredFavorites();
	if (favorites.length === 0) {
		return;
	}

	// Add separator
	const separator = document.createElement("hr");
	separator.id = SEPARATOR_ID;
	dropdown.appendChild(separator);

	// Add favorites, with sorting
	const sorted = [...favorites].sort((a, b) =>
		a.localeCompare(b, undefined, { sensitivity: "base" }),
	);
	for (const subredditName of sorted) {
		const url = `/r/${subredditName}`;
		const item = document.createElement("li");
		item.className = FAVORITE_ITEM_CLASS;
		const link = document.createElement("a");
		link.text = url;
		link.href = url;
		item.appendChild(link);
		dropdown.appendChild(item);
	}
}

function initFavorites() {
	const favoriteElement = document.getElementById(FAVORITE_LINK_ID);
	if (favoriteElement) {
		const subredditName = favoriteElement.dataset.element;
		toggleFavoriteTextButton(isFavorite(subredditName));
	}
	updateFavoritesDropdown();
}

if (document.readyState !== "loading") {
	initFavorites();
} else {
	document.addEventListener("DOMContentLoaded", () => {
		initFavorites();
	});
}
