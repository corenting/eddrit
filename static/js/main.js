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

        // Refresh video player setup
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
    fetch("/api/comments/xhr?subreddit=" + subredditName  + "&post_id=" + postId + "&comment_id=" + commentIdParam)
    .then(function(response) {
      return response.text();
    })
    .then(function(text) {
        parentElt.innerHTML = text
    });
}

// Indigo player setup
function setupVideo(videoElement) {
    if (videoElement) {

        // Get video config
        const src = videoElement.getAttribute("data-src");
        const type = videoElement.getAttribute("data-type");
        const width = parseInt(videoElement.getAttribute("data-width"));
        const height = parseInt(videoElement.getAttribute("data-height"));
        const poster = videoElement.getAttribute("data-poster");
        const autoplay = videoElement.getAttribute("data-autoplay") === "True";

        // Setup player
        const config = {
            autoplay: autoplay,
            volume: autoplay ? 0 : 1,
            aspectRatio: width/height,
            ui: { image: poster },
            sources: [
              {
                type: type,
                src: src,
              }
            ],
        };

        IndigoPlayer.setChunksPath(window.location.origin + "/static/vendors/indigo-player/");
        player = IndigoPlayer.init(videoElement, config);

        // If autoplay, loop too
        player.on(IndigoPlayer.Events.STATE_ENDED, () => {
            player.seekTo(0);
            player.play();
        });
    }
}

// Init
if( document.readyState !== 'loading' ) {
    initPage();
} else {
    document.addEventListener('DOMContentLoaded', function () {
        initPage();
    });
}

function initPage() {
    // Init video players
    var elements = document.getElementsByClassName('post-video');
    for (var i = 0; i < elements.length; ++i) {
        var video = elements[i];
        setupVideo(video)
    }
}
