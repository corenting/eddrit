// Toggle content button logic
function togglePostVisibility(postId) {
	// Get root elements
	const rootElement = document.getElementById(`content-${postId}`);
	const buttonLink = document.getElementById(`post-preview-button-${postId}`);

	// Get content HTML from attribute
	const contentTemplate = document.getElementById(`content-${postId}-template`);

	if (rootElement.style.display === "none") {
		rootElement.style.display = "inherit";
		buttonLink.innerText = "-";

		// Copy template and append it
		const content = contentTemplate.content.cloneNode(true);
		rootElement.appendChild(content);

		setupVideo(document.getElementById(`video-${postId}`));
	} else {
		rootElement.style.display = "none";
		buttonLink.innerText = "+";

		// Destroy content
		const content = document.getElementById(`content-${postId}-preview`);
		rootElement.removeChild(content);
	}

	setupGallery(document.getElementById(`gallery-${postId}`));
}

// Toggle logic for comment
function toggleCommentVisibility(commentId) {
	const contentElement = document.getElementById(
		`comment-${commentId}-content`,
	);
	const childrenElement = document.getElementById(
		`comment-${commentId}-children`,
	);
	const toggleElement = document.getElementById(`comment-${commentId}-toggle`);

	if (contentElement.style.display === "none") {
		contentElement.style.display = "inherit";
		childrenElement.style.display = "inherit";
		toggleElement.innerText = "[-]";
	} else {
		contentElement.style.display = "none";
		childrenElement.style.display = "none";
		toggleElement.innerText = "[+]";
	}
}

// Logic for fetching more comments
function fetchCommentsChildren(
	subredditName,
	postId,
	parentId,
	commentId,
	depth,
) {
	// We get the parent element, but the XHR return the <ul> so get the parent ul element
	const commentElt = document.getElementById(`comment-${parentId}`);
	const commentIdParam = postId === parentId ? commentId : parentId;

	fetch(
		`/xhr/comments/xhr?subreddit=${subredditName}&post_id=${postId}&comment_id=${commentIdParam}&depth=${depth}`,
	)
		.then((response) => response.text())
		.then((text) => {
			// Parse new content
			const parser = new DOMParser();
			const newCommentElement = parser
				.parseFromString(text, "text/html")
				.getElementsByTagName("li")[0];

			commentElt.replaceWith(newCommentElement);
		});
}

// Video player setup
function setupVideo(videoElement) {
	if (!videoElement) {
		return;
	}

	const videos = JSON.parse(videoElement.getAttribute("data-content")).videos;
	const player = videojs(videoElement, {
		controls: true,
		fill: true,
		autoplay: false,
		loop: false,
		sources: videos.map((x) => {
			return {
				src: x.url,
				type: x.video_format,
				is_gif: x.is_gif,
				width: x.width,
				height: x.height,
			};
		}),
	});

	player.on("sourceset", () => {
		// Sometimes source returned from currentSource doesn't include
		// the custom metadata, so get it from the original sources
		let currentSource = player.currentSource();
		if (currentSource.is_gif === undefined) {
			currentSource = player
				.currentSources()
				.find((x) => x.src === currentSource.src);
		}

		console.debug("Switched to source", currentSource);
		player.autoplay(currentSource.is_gif);
		player.loop(currentSource.is_gif);

		videoElement.setAttribute("width", currentSource.width);
		videoElement.setAttribute("height", currentSource.height);
	});
}

// Gallery setup
function setupGallery(galleryElement) {
	if (!galleryElement) {
		return;
	}

	// Hide all elements except first
	const picturesElements = galleryElement.getElementsByClassName(
		"post-content-gallery-picture",
	);
	const captionsElements = galleryElement.getElementsByClassName(
		"post-content-gallery-caption",
	);
	for (let i = 1; i < picturesElements.length; ++i) {
		picturesElements[i].style.display = "none";
		captionsElements[i].style.display = "none";
	}

	// Mask previous button
	const previousButton = galleryElement.getElementsByClassName(
		"post-content-gallery-previous-button",
	)[0];
	previousButton.removeAttribute("href");
}

// On gallery button click
function onGalleryButtonClick(postId, move) {
	const parentElement = document.getElementById(`gallery-${postId}`);
	const picturesElements = [
		...parentElement.getElementsByClassName("post-content-gallery-picture"),
	];
	const captionsElements = [
		...parentElement.getElementsByClassName("post-content-gallery-caption"),
	];

	// Get current displayed and current index
	const currentDisplayedElement = picturesElements.find((element) => {
		return element.style.display !== "none";
	});
	const currentIndex = parseInt(currentDisplayedElement.id);
	const newIndex = currentIndex + move;

	// Update text
	const textElement = parentElement.getElementsByClassName(
		"post-content-gallery-numbers",
	)[0];
	textElement.innerHTML = `${newIndex + 1} / ${picturesElements.length}`;

	// Display correct picture
	for (let i = 0; i < picturesElements.length; ++i) {
		const displayMode = i === newIndex ? "unset" : "none";
		picturesElements[i].style.display = displayMode;
		captionsElements[i].style.display = displayMode;
	}

	// Previous button
	const previousButton = parentElement.getElementsByClassName(
		"post-content-gallery-previous-button",
	)[0];
	previousButton.setAttribute("disabled", newIndex === 0);
	if (newIndex === 0) {
		previousButton.setAttribute("disabled", "");
	} else {
		previousButton.removeAttribute("disabled");
	}

	// Next button
	const nextButton = parentElement.getElementsByClassName(
		"post-content-gallery-next-button",
	)[0];
	if (newIndex === picturesElements.length - 1) {
		nextButton.setAttribute("disabled", "");
	} else {
		nextButton.removeAttribute("disabled");
	}
}

function initPage() {
	// Init video players
	const videoElements = document.getElementsByClassName("video-js");
	for (let i = 0; i < videoElements.length; ++i) {
		const video = videoElements[i];
		setupVideo(video);
	}

	// Init gallery posts
	const galleryElements = document.getElementsByClassName(
		"post-content-gallery",
	);
	for (let i = 0; i < galleryElements.length; ++i) {
		const gallery = galleryElements[i];
		setupGallery(gallery);
	}
}

// Init
if (document.readyState !== "loading") {
	initPage();
} else {
	document.addEventListener("DOMContentLoaded", () => {
		initPage();
	});
}
