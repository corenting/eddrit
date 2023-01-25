// Toggle content button logic
function togglePostVisibility(postId) {
    // Get root elements
    var rootElement = document.getElementById("content-" + postId);
    var buttonLink = document.getElementById("post-preview-button-" + postId);

    // Get content HTML from attribute
    var contentTemplate = document.getElementById("content-" + postId + "-template");

    if (rootElement.style.display === "none") {
        rootElement.style.display = "inherit";
        buttonLink.innerText = "-";

        // Copy template and append it
        const content = contentTemplate.content.cloneNode(true);
        rootElement.appendChild(content);

        setupVideo(document.getElementById("video-" + postId));
    } else {
        rootElement.style.display = "none";
        buttonLink.innerText = "+";

        // Destroy content
        var content = document.getElementById("content-" + postId + "-preview");
        rootElement.removeChild(content);
    }

    setupGallery(document.getElementById("gallery-" + postId));
}

// Toggle logic for comment
function toggleCommentVisibility(commentId) {
    var contentElement = document.getElementById("comment-" + commentId + "-content");
    var childrenElement = document.getElementById("comment-" + commentId + "-children");
    var toggleElement = document.getElementById("comment-" + commentId + "-toggle");

    if (contentElement.style.display === "none") {
        contentElement.style.display = "inherit";
        childrenElement.style.display = "inherit";
        toggleElement.innerText = "[-]"
    } else {
        contentElement.style.display = "none";
        childrenElement.style.display = "none";
        toggleElement.innerText = "[+]"
    }
}

// Logic for fetching more comments
function fetchCommentsChildren(subredditName, postId, parentId, commentId, depth) {
    // We get the parent element, but the XHR return the <ul> so get the parent ul element
    var commentElt = document.getElementById("comment-" + parentId);
    var commentIdParam = postId == parentId ? commentId : parentId

    fetch("/xhr/comments/xhr?subreddit=" + subredditName + "&post_id=" + postId + "&comment_id=" + commentIdParam + "&depth=" + depth)
        .then(function (response) {
            return response.text();
        })
        .then(function (text) {

            // Parse new content
            var parser = new DOMParser();
            var newCommentElement = parser.parseFromString(text, 'text/html').getElementsByTagName('li')[0];

            commentElt.replaceWith(newCommentElement)
        });
}

// Video player setup
function setupVideo(videoElement) {
    if (!videoElement) {
        return;
    }

    let isGif = videoElement.getAttribute('data-is-gif') == 'True';
    videojs(videoElement, {
        'controls': true,
        'fill': true,
        'autoplay': isGif,
        'sources': [{
            'type': videoElement.getAttribute('data-video-format'),
            'src': videoElement.getAttribute('data-url')
        }]
    });
}

// Gallery setup
function setupGallery(galleryElement) {
    if (!galleryElement) {
        return;
    }

    // Hide all elements except first
    var picturesElements = galleryElement.getElementsByClassName('post-content-gallery-picture');
    for (var i = 1; i < picturesElements.length; ++i) {
        picturesElements[i].style.display = "none";
    }

    // Mask previous button
    var previousButton = galleryElement.getElementsByClassName("post-content-gallery-previous-button")[0];
    previousButton.removeAttribute("href");
}

// On gallery button click
function onGalleryButtonClick(postId, move) {
    var parentElement = document.getElementById("gallery-" + postId);
    var picturesElements = [...parentElement.getElementsByClassName('post-content-gallery-picture')];

    // Get current displayed and current index
    var currentDisplayedElement = picturesElements.find(element => {
        return element.style.display !== "none";
    });
    var currentIndex = parseInt(currentDisplayedElement.id);
    var newIndex = currentIndex + move;

    // Update text
    var textElement = parentElement.getElementsByClassName("post-content-gallery-numbers")[0];
    textElement.innerHTML = `${newIndex + 1} / ${picturesElements.length}`;

    // Display correct picture
    for (var i = 0; i < picturesElements.length; ++i) {
        picturesElements[i].style.display = i === newIndex ? "unset" : "none";
    }

    // Previous button
    var previousButton = parentElement.getElementsByClassName("post-content-gallery-previous-button")[0];
    if (newIndex === 0) {
        previousButton.removeAttribute("href");
    }
    else {
        previousButton.setAttribute("href", "#!")
    }

    // Next button
    var nextButton = parentElement.getElementsByClassName("post-content-gallery-next-button")[0];
    if (newIndex === picturesElements.length - 1) {
        nextButton.removeAttribute("href");
    }
    else {
        nextButton.setAttribute("href", "#!")
    }
}

function initPage() {
    // Init video players
    var videoElements = document.getElementsByClassName('video-js');
    for (var i = 0; i < videoElements.length; ++i) {
        var video = videoElements[i];
        setupVideo(video);
    }

    // Init gallery posts
    var galleryElements = document.getElementsByClassName('post-content-gallery');
    for (var i = 0; i < galleryElements.length; ++i) {
        var gallery = galleryElements[i];
        setupGallery(gallery);
    }
}

// Init
if (document.readyState !== 'loading') {
    initPage();
} else {
    document.addEventListener('DOMContentLoaded', function () {
        initPage();
    });
}
