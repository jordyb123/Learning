const form = document.getElementById("github-form");
const input = document.getElementById("github-input");
const messageArea = document.getElementById("message-area");
const profileResults = document.getElementById("profile-results");

function showMessage(msg, type="info") {
    messageArea.textContent = msg;
    messageArea.className = type;
}

function clearProfile() {
    profileResults.textContent = "";
    profileResults.className = ""
}

function clearMessage() {
    messageArea.textContent = "";
    messageArea.className = "";
}



async function fetchGitHubProfile(username) {
    clearProfile();
    try {
        showMessage("Loading profile...", "info");

        const response = await fetch(`https://api.github.com/users/${username}`);

        if (response.status === 404) {
            showMessage("User not found", "error");
            profileResults.innerHTML = "";
            return;
        }

        if (!response.ok) {
            showMessage("Could not fetch profile", "error");
            profileResults.innerHTML = "";
            return;
        }

        const data = await response.json();
        showMessage("Profile loaded!", "success");

        renderProfile(data);
    } catch (error) {
        showMessage("Network error", "error");
        profileResults.innerHTML = "";
    } 
}

function renderProfile(profile) {
    profileResults.innerHTML = `
        <div class="profile-card">
            <img src="${profile.avatar_url}" class="avatar" />
            <h2>${profile.name || profile.login}</h2>
            <p>${profile.bio || "No bio available"}</p>
            <p><strong>Followers:</strong> ${profile.followers}</p>
            <p><strong>Following:</strong> ${profile.following}</p>
            <p><strong>Public Repos:</strong> ${profile.public_repos}</p>
            <a href="${profile.html_url}" target="_blank">View on GitHub</a>
        </div>
    `;
}

form.addEventListener("submit", (event) => {
    event.preventDefault();

    const text = input.value.trim();
    if (text === "") {
        showMessage("Input cannot be empty", "error")
        return;
    }

    clearMessage();
    fetchGitHubProfile(text);
});
