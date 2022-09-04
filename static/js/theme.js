const THEME_SYSTEM = "system";
const THEME_LIGHT = "system";
const THEME_DARK = "system";

const DARK_MODE_MEDIA_QUERY = window.matchMedia('(prefers-color-scheme: dark)');
const THEME_LOCAL_STORAGE_KEY = 'theme';

function setTheme(theme) {
    window.localStorage.setItem(THEME_LOCAL_STORAGE_KEY, theme);
    if (theme != THEME_SYSTEM) {
        document.getElementsByTagName('html')[0].setAttribute('data-theme', theme);
    }
    else {
        document.getElementsByTagName('html')[0].removeAttribute('data-theme');
    }
};

function getActiveTheme() {
    // Check user preference first
    let userTheme = window.localStorage.getItem(THEME_LOCAL_STORAGE_KEY);
    if (userTheme) {
        return userTheme;
    }

    // Else check media query theme
    return DARK_MODE_MEDIA_QUERY.matches ? THEME_DARK : THEME_LIGHT;
};

function setupSettingsPage() {
    let selectElement = document.getElementById('settings-theme-select');

    // If no element, we are not on the settings page
    if (selectElement == null) {
        return;
    }

    // Set correct value in select
    let currentTheme = getActiveTheme();
    selectElement.value = currentTheme[0].toUpperCase() + currentTheme.substring(1);

    // Add listener for theme change
    selectElement.addEventListener('change', function () {
        let selectedTheme = selectElement.value.toLowerCase();
        // handle system theme choice
        if (selectedTheme == '') {
            selectedTheme = THEME_SYSTEM;
        }
        setTheme(selectedTheme);
    });
}

// On init
setTheme(getActiveTheme());
setupSettingsPage();
