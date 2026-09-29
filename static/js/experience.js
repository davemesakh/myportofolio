function experienceElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
}

function appendExperiencePeriod(container, period) {
    if (!period) return;
    const time = experienceElement("time", null, period.label);
    time.setAttribute("datetime", period.iso);
    container.appendChild(time);
}

function experiencePostForm(action, csrfToken) {
    const form = experienceElement("form");
    form.method = "post";
    form.action = action;
    const token = experienceElement("input");
    token.type = "hidden";
    token.name = "csrfmiddlewaretoken";
    token.value = csrfToken;
    form.appendChild(token);
    return form;
}

function buildExperienceCardElement(item, isAuthenticated, csrfToken) {
    const card = experienceElement("article", "experience-item");

    if (item.logo_url) {
        try {
            const logoUrl = new URL(item.logo_url, window.location.href);
            if (logoUrl.origin === window.location.origin && /^https?:$/.test(logoUrl.protocol)) {
                const logo = experienceElement("img", "experience-logo");
                logo.src = logoUrl.href;
                logo.alt = item.logo_alt || "";
                logo.width = 88;
                logo.height = 88;
                logo.loading = "lazy";
                card.appendChild(logo);
            }
        } catch (error) {
            // Ignore malformed logo paths; the card remains readable without an image.
        }
    }

    const header = experienceElement("header", "experience-header");
    const identity = experienceElement("div", "experience-identity");
    if (item.organization) {
        identity.appendChild(experienceElement("h3", "experience-organization", item.organization));
        identity.appendChild(experienceElement("p", "experience-role", item.title));
    } else {
        identity.appendChild(experienceElement("h3", "experience-organization", item.title));
    }
    header.appendChild(identity);

    if (item.start_period || item.end_period || item.is_current) {
        const period = experienceElement("p", "experience-period");
        appendExperiencePeriod(period, item.start_period);
        if (item.is_current) {
            if (item.start_period) period.appendChild(document.createTextNode(" – "));
            period.appendChild(document.createTextNode("Present"));
        } else if (item.end_period) {
            if (item.start_period) period.appendChild(document.createTextNode(" – "));
            appendExperiencePeriod(period, item.end_period);
        }
        header.appendChild(period);
    }
    card.appendChild(header);

    const contributions = experienceElement("div", "experience-contributions");
    for (const paragraph of item.description_paragraphs) {
        contributions.appendChild(experienceElement("p", null, paragraph));
    }

    const star = experienceElement("div", "experience-star");
    if (isAuthenticated && item.star_url && csrfToken) {
        const form = experiencePostForm(item.star_url, csrfToken);
        const action = item.is_starred ? "Unstar" : "Star";
        const button = experienceElement(
            "button",
            `award-cancel experience-star-button${item.is_starred ? " is-starred" : ""}`,
            action
        );
        button.type = "submit";
        button.setAttribute("aria-label", `${action} ${item.title}`);
        form.appendChild(button);
        star.appendChild(form);
    }
    const count = item.star_count;
    star.appendChild(experienceElement(
        "span", "experience-star-count", `★ ${count} star${count === 1 ? "" : "s"}`
    ));
    contributions.appendChild(star);

    if (item.can_edit && item.edit_url) {
        const actions = experienceElement("div", "award-form-actions experience-item-actions");
        const edit = experienceElement("a", "award-cancel", "Edit");
        edit.href = item.edit_url;
        actions.appendChild(edit);
        if (item.can_delete && item.delete_url && csrfToken) {
            const form = experiencePostForm(item.delete_url, csrfToken);
            const button = experienceElement("button", "award-delete-confirm", "Delete");
            button.type = "submit";
            button.setAttribute("aria-label", `Delete ${item.title}`);
            form.appendChild(button);
            actions.appendChild(form);
        }
        contributions.appendChild(actions);
    }
    card.appendChild(contributions);
    return card;
}

const SEARCH_DEBOUNCE_DELAY = 300;
let searchDebounceTimer;
let experiencesAbortController;

async function fetchExperiences(searchQuery = "") {
    const grid = document.getElementById("experience-list");
    const loading = document.getElementById("experience-loading");
    const empty = document.getElementById("experience-empty");
    const error = document.getElementById("experience-error");
    if (!grid || !loading || !empty || !error) return;

    loading.hidden = false;
    grid.hidden = true;
    empty.hidden = true;
    error.hidden = true;

    if (experiencesAbortController) experiencesAbortController.abort();
    const controller = new AbortController();
    experiencesAbortController = controller;
    const url = searchQuery
        ? `${grid.dataset.url}?title=${encodeURIComponent(searchQuery)}`
        : grid.dataset.url;

    try {
        const response = await fetch(url, { signal: controller.signal });
        if (!response.ok) throw new Error(`Experience request failed: ${response.status}`);
        const payload = await response.json();
        if (!Array.isArray(payload.experiences)) throw new Error("Invalid Experience response");
        if (controller !== experiencesAbortController) return;

        grid.replaceChildren();
        const csrfToken = document.getElementById("experience-csrf-token")?.value;
        for (const item of payload.experiences) {
            grid.appendChild(buildExperienceCardElement(item, payload.is_authenticated, csrfToken));
        }
        grid.hidden = payload.experiences.length === 0;
        empty.textContent = searchQuery
            ? "No experiences match your search."
            : "Belum ada pengalaman yang ditambahkan.";
        empty.hidden = payload.experiences.length !== 0;
    } catch (fetchError) {
        if (fetchError.name === "AbortError" || controller !== experiencesAbortController) return;
        grid.replaceChildren();
        error.hidden = false;
    } finally {
        if (controller === experiencesAbortController) {
            loading.hidden = true;
            experiencesAbortController = undefined;
        }
    }
}

const searchForm = document.getElementById("experience-search-form");
const searchInput = document.getElementById("experience-search-input");

function searchExperiences() {
    if (searchInput) fetchExperiences(searchInput.value.trim());
}

if (searchForm && searchInput) {
    searchInput.addEventListener("input", () => {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(searchExperiences, SEARCH_DEBOUNCE_DELAY);
    });
    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearTimeout(searchDebounceTimer);
        searchExperiences();
    });
}

fetchExperiences("");
