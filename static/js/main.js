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

	const videos = JSON.parse(videoElement.getAttribute("data-videos"));

	const player = videojs(videoElement, {
		controls: true,
		fill: true,
		autoplay: false,
		loop: false,
		poster: videos[0].poster_url,
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

// Gallery: display or not element
function displayGalleryElement(postId, currentIndex) {
	// Get content template and create content node
	const contentTemplate = document.getElementById(
		`post-${postId}-content-gallery-template-${currentIndex}`,
	);
	const content = contentTemplate.content.cloneNode(true);
	content.children[0].dataset.currentIndex = currentIndex;
	content.children[0].id = `post-${postId}-content-displayed-gallery-item`;

	// Get container node, clean it and put content
	const container = document.getElementById(
		`post-${postId}-content-gallery-item`,
	);
	container.innerHTML = "";
	container.appendChild(content);

	// Init video players if gallery post is a video
	const videoElements = document.getElementsByClassName("video-js");
	for (let i = 0; i < videoElements.length; ++i) {
		const video = videoElements[i];
		setupVideo(video);
	}
}

// Gallery setup
function setupGallery(galleryElement) {
	if (!galleryElement) {
		return;
	}

	displayGalleryElement(galleryElement.dataset.postId, 0); // display the first element
}

// On gallery button click
function onGalleryButtonClick(postId, move) {
	const parentElement = document.getElementById(`gallery-${postId}`);
	const totalLength = Number.parseInt(parentElement.dataset.totalLength);

	// Get current displayed and current index
	const currentDisplayedElement = document.getElementById(
		`post-${postId}-content-displayed-gallery-item`,
	);
	const currentIndex = Number.parseInt(
		currentDisplayedElement.dataset.currentIndex,
	);
	const newIndex = currentIndex + move;

	// Update text
	const textElement = parentElement.getElementsByClassName(
		"post-content-gallery-numbers",
	)[0];
	textElement.innerHTML = `${newIndex + 1} / ${totalLength}`;

	// Display correct content
	displayGalleryElement(postId, newIndex);

	// Previous button
	const previousButton = parentElement.getElementsByClassName(
		"post-content-gallery-previous-button",
	)[0];
	if (newIndex === 0) {
		previousButton.setAttribute("disabled", "");
	} else {
		previousButton.removeAttribute("disabled");
	}

	// Next button
	const nextButton = parentElement.getElementsByClassName(
		"post-content-gallery-next-button",
	)[0];
	if (newIndex === totalLength - 1) {
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
