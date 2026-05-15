(() => {
	var checkbox = document.getElementById("sidebar-toggle");
	var details = document.querySelector(".sidebar-mobile-toggle");
	if (!checkbox && !details) {
		return;
	}

	function save(closed) {
		try {
			localStorage.setItem("eddrit:sidebar-closed", closed ? "true" : "false");
		} catch (_e) {
			/* localStorage unavailable (private mode, quota, etc.) — no-op. */
		}
	}

	if (checkbox) {
		checkbox.addEventListener("change", () => {
			save(checkbox.checked);
		});
	}

	if (details) {
		details.addEventListener("toggle", () => {
			save(!details.open);
		});
	}
})();
