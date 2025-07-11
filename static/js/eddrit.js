// If content has an image, set src from data-src
// as it was put there to avoid Firefox loading it when the template is not used
function setSrcForContentImageIfNeeded(content) {
	const imageElements = content.children[0].getElementsByTagName("img");
	if (imageElements.length > 0) {
		if (imageElements[0].src === undefined || imageElements[0].src === "") {
			imageElements[0].src = imageElements[0].dataset.src;
		}
	}
}

// Toggle content button logic
// biome-ignore lint/correctness/noUnusedVariables: used from template
function togglePostVisibility(postId) {
	// Get root elements
	const rootElement = document.getElementById(`content-${postId}`);
	const buttonLink = document.getElementById(`post-preview-button-${postId}`);

	if (rootElement.style.display === "none") {
		rootElement.style.display = "inherit";
		buttonLink.innerText = "-";

		// Get content HTML from template and copy it to append
		const contentTemplate = document.getElementById(
			`content-${postId}-template`,
		);
		const content = contentTemplate.content.cloneNode(true);
		setSrcForContentImageIfNeeded(content);
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
// biome-ignore lint/correctness/noUnusedVariables: used from template
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
// biome-ignore lint/correctness/noUnusedVariables: used from template
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
		autoplay: false,
		fill: true,
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

// Gallery: display or not element
function displayGalleryElement(postId, currentIndex) {
	// Get content template and create content node
	const contentTemplate = document.getElementById(
		`post-${postId}-content-gallery-template-${currentIndex}`,
	);
	const content = contentTemplate.content.cloneNode(true);
	content.children[0].dataset.currentIndex = currentIndex;
	content.children[0].id = `post-${postId}-content-displayed-gallery-item`;

	setSrcForContentImageIfNeeded(content);

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
// biome-ignore lint/correctness/noUnusedVariables: used from template
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
	console.info("Page loaded, setting up media");
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
