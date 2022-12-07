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
function fetchCommentsChildren(subredditName, postId, parentId, commentId) {
    var parentElt = document.getElementById("comment-" + parentId);

    var commentIdParam = postId == parentId ? commentId : parentId
    fetch("/xhr/comments/xhr?subreddit=" + subredditName + "&post_id=" + postId + "&comment_id=" + commentIdParam)
        .then(function (response) {
            return response.text();
        })
        .then(function (text) {
            parentElt.innerHTML = text
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

function initPage() {
    // Init video players
    var videoElements = document.getElementsByClassName('video-js');
    for (var i = 0; i < videoElements.length; ++i) {
        var video = videoElements[i];
        setupVideo(video);
    }

    // Show js-only elements
    var jsOnlyElements = document.getElementsByClassName('js-only');
    for (var i = 0; i < jsOnlyElements.length; ++i) {
        var element = jsOnlyElements[i];
        element.style.display = "unset";
    }

    // Hide no-js-only elements
    var noJsOnlyElements = document.getElementsByClassName('js-only');
    for (var i = 0; i < noJsOnlyElements.length; ++i) {
        var element = noJsOnlyElements[i];
        element.style.display = "none";
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
