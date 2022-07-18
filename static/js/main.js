// Toggle content button logic
function togglePostVisibility(postId) {
    // Get root elements
    var rootElement = document.getElementById("content-" + postId);
    var buttonImg = document.getElementById("toggle-" + postId);

    // Get content HTML from attribute
    var contentTemplate = document.getElementById("content-" + postId + "-template");

    if (rootElement.style.display === "none") {
        rootElement.style.display = "block";
        buttonImg.src = buttonImg.src.replace("plus", "dash");

        // Copy template and append it
        const content = contentTemplate.content.cloneNode(true);
        rootElement.appendChild(content);

        setupVideo(document.getElementById("video-" + postId));
    } else {
        rootElement.style.display = "none";
        buttonImg.src = buttonImg.src.replace("dash", "plus");

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
        contentElement.style.display = "block";
        childrenElement.style.display = "block";
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

    let width = parseInt(videoElement.getAttribute('data-width'));
    let height = parseInt(videoElement.getAttribute('data-height'));
    let isGif = videoElement.getAttribute('data-is-gif') == 'True';
    videojs(videoElement, {
        'width': width,
        'height': height,
        'controls': !isGif,
        'autoplay': isGif,
        'sources': [{
            'type': videoElement.getAttribute('data-video-format'),
            'src': videoElement.getAttribute('data-url')
        }]
    });
}

function initPage() {
    // Init video players
    var elements = document.getElementsByClassName('post-video');
    for (var i = 0; i < elements.length; ++i) {
        var video = elements[i];
        setupVideo(video);
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
