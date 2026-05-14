(function () {
	"use strict";

	var checkbox = document.getElementById("sidebar-toggle");
	var details = document.querySelector(".sidebar-mobile-toggle");
	if (!checkbox && !details) {
		return;
	}

	function save(closed) {
		try {
			localStorage.setItem("eddrit:sidebar-closed", closed ? "true" : "false");
		} catch (e) {
			/* localStorage unavailable (private mode, quota, etc.) — no-op. */
		}
	}

	if (checkbox) {
		checkbox.addEventListener("change", function () {
			save(checkbox.checked);
		});
	}

	if (details) {
		details.addEventListener("toggle", function () {
			save(!details.open);
		});
	}
})();
