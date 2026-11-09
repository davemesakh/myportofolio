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

const experienceApi = document.getElementById("experience-api-config")?.dataset;
const EXPERIENCE_UUID_PLACEHOLDER = "00000000-0000-0000-0000-000000000000";

function experienceUrl(pattern, id) {
    return pattern.replace(EXPERIENCE_UUID_PLACEHOLDER, encodeURIComponent(id));
}

function buildExperienceCardElement(item) {
    const card = experienceElement("article", "experience-item");

    if (item.logo_url) {
        try {
            const logoUrl = new URL(item.logo_url, window.location.href);
            if (logoUrl.protocol === "https:" ||
                (logoUrl.protocol === "http:" && logoUrl.origin === window.location.origin)) {
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
    if (experienceApi.authenticated === "true") {
        const action = item.is_starred ? "Unstar" : "Star";
        const button = experienceElement(
            "button",
            `award-cancel experience-star-button${item.is_starred ? " is-starred" : ""}`,
            action
        );
        button.type = "button";
        button.setAttribute("aria-label", `${action} ${item.title}`);
        button.setAttribute("aria-pressed", String(item.is_starred));
        button.addEventListener("click", () => toggleExperienceStar(item, button));
        star.appendChild(button);
    } else {
        const login = experienceElement("a", "award-cancel", "Log in to star");
        login.href = experienceApi.loginUrl;
        star.appendChild(login);
    }
    const count = item.star_count;
    star.appendChild(experienceElement(
        "span", "experience-star-count", `★ ${count} star${count === 1 ? "" : "s"}`
    ));
    contributions.appendChild(star);

    if (experienceApi.canEdit.trim() === "true") {
        const actions = experienceElement("div", "award-form-actions experience-item-actions");
        const edit = experienceElement("a", "award-cancel", "Edit");
        edit.href = experienceUrl(experienceApi.editUrl, item.id);
        actions.appendChild(edit);
        if (experienceApi.superuser === "true") {
            const button = experienceElement("button", "award-delete-confirm", "Delete");
            button.type = "button";
            button.setAttribute("aria-label", `Delete ${item.title}`);
            button.addEventListener("click", () => deleteExperience(item, button));
            actions.appendChild(button);
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
    if (!grid || !loading || !empty || !error || !experienceApi) return;

    loading.hidden = false;
    grid.hidden = true;
    empty.hidden = true;
    error.hidden = true;

    if (experiencesAbortController) experiencesAbortController.abort();
    const controller = new AbortController();
    experiencesAbortController = controller;
    const url = searchQuery
        ? `${experienceApi.listUrl}?title=${encodeURIComponent(searchQuery)}`
        : experienceApi.listUrl;

    try {
        const response = await fetch(url, {
            signal: controller.signal,
            credentials: "same-origin",
            headers: { Accept: "application/json" },
        });
        if (!response.ok) throw new Error(`Experience request failed: ${response.status}`);
        const payload = await response.json();
        if (!Array.isArray(payload)) throw new Error("Invalid Experience response");
        if (controller !== experiencesAbortController) return;

        grid.replaceChildren();
        for (const item of payload) {
            grid.appendChild(buildExperienceCardElement(item));
        }
        grid.hidden = payload.length === 0;
        empty.textContent = searchQuery
            ? "No experiences match your search."
            : "Belum ada pengalaman yang ditambahkan.";
        empty.hidden = payload.length !== 0;
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

function closeExperienceModal() {
    const modal = document.getElementById("add-experience-modal");
    if (modal?.matches(":popover-open")) modal.hidePopover();
}

function getCookie(name) {
    const cookie = document.cookie.split("; ").find((part) => part.startsWith(`${name}=`));
    return cookie ? decodeURIComponent(cookie.slice(name.length + 1)) : null;
}

function experienceErrorMessage(result, status) {
    if (result && typeof result === "object") {
        const messages = Object.entries(result).flatMap(([field, errors]) => {
            const entries = Array.isArray(errors) ? errors : [errors];
            return entries.filter((entry) => typeof entry === "string").map((message) =>
                field === "detail" || field === "non_field_errors"
                    ? message
                    : `${field.replaceAll("_", " ")}: ${message}`
            );
        });
        if (messages.length) return messages.join(" ");
    }
    return `Request failed (HTTP ${status}). Please refresh the page and try again.`;
}

async function experienceApiRequest(url, method, payload) {
    const headers = { Accept: "application/json", "X-CSRFToken": getCookie("csrftoken") || "" };
    if (payload !== undefined) headers["Content-Type"] = "application/json";
    let response;
    try {
        response = await fetch(url, {
            method,
            credentials: "same-origin",
            headers,
            ...(payload !== undefined ? { body: JSON.stringify(payload) } : {}),
        });
    } catch (error) {
        throw new Error("A network error occurred. Check the list before retrying the action.");
    }
    const data = response.status === 204 ? null : await response.json().catch(() => null);
    if (!response.ok) {
        const error = new Error(experienceErrorMessage(data, response.status));
        error.status = response.status;
        throw error;
    }
    return { status: response.status, data };
}

function refreshExperienceSearch() {
    clearTimeout(searchDebounceTimer);
    return fetchExperiences(searchInput?.value.trim() || "");
}

function experienceFormPayload(form) {
    const payload = {};
    for (const name of ["title", "description", "category", "organization", "logo_static_path", "logo_alt"]) {
        payload[name] = form.elements.namedItem(name).value;
    }
    for (const name of ["start_year", "start_month", "end_year", "end_month", "display_order"]) {
        const value = form.elements.namedItem(name).value.trim();
        if (value === "") {
            // display_order has a model default; the date integers are nullable.
            if (name !== "display_order") payload[name] = null;
        } else {
            const number = Number(value);
            if (!Number.isInteger(number)) throw new Error(`${name.replaceAll("_", " ")}: Enter a whole number.`);
            payload[name] = number;
        }
    }
    const current = form.elements.namedItem("is_current");
    if (current.type === "checkbox") {
        payload.is_current = current.checked;
    } else {
        // Django's NullBooleanSelect uses "unknown", "true", and "false".
        payload.is_current = current.value === "true" ? true : current.value === "false" ? false : null;
    }
    return payload;
}

async function toggleExperienceStar(item, button) {
    if (button.disabled) return;
    button.disabled = true;
    try {
        const result = await experienceApiRequest(experienceUrl(experienceApi.starUrl, item.id), "POST");
        if (result.status !== 200 || result.data?.id !== item.id) {
            throw new Error("Unexpected server response. Check the list before trying again.");
        }
        showToast("Success", result.data.is_starred ? "Experience starred!" : "Experience unstarred!", "success");
        await refreshExperienceSearch();
    } catch (error) {
        showToast("Could not update star", error.message, "error");
    } finally {
        button.disabled = false;
    }
}

async function deleteExperience(item, button) {
    if (button.disabled || !window.confirm(`Delete ${item.title}? This cannot be undone.`)) return;
    button.disabled = true;
    try {
        const result = await experienceApiRequest(experienceUrl(experienceApi.detailUrl, item.id), "DELETE");
        if (result.status !== 204) {
            throw new Error("Unexpected server response. Check the list before trying again.");
        }
        showToast("Success", "Experience successfully deleted!", "success");
        await refreshExperienceSearch();
    } catch (error) {
        showToast("Could not delete Experience", error.message, "error");
    } finally {
        button.disabled = false;
    }
}

async function addExperience(event) {
    event.preventDefault();
    const experienceForm = event.currentTarget;
    const submitButton = experienceForm.querySelector('button[type="submit"]');
    if (submitButton?.disabled) return;
    if (submitButton) submitButton.disabled = true;

    try {
        const result = await experienceApiRequest(experienceApi.listUrl, "POST", experienceFormPayload(experienceForm));
        if (result.status !== 201 || !result.data?.id) {
            throw new Error("Unexpected server response. Check the Experience list before trying again.");
        }

        experienceForm.reset();
        closeExperienceModal();
        showToast("Success", "Experience successfully added!", "success");
        await refreshExperienceSearch();
    } catch (error) {
        showToast("Failed to add Experience", error.message, "error");
    } finally {
        if (submitButton) submitButton.disabled = false;
    }
}

const experienceForm = document.getElementById("add-experience-form");
if (experienceForm) experienceForm.addEventListener("submit", addExperience);

async function editExperience(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton.disabled) return;
    submitButton.disabled = true;

    try {
        const payload = experienceFormPayload(form);
        const result = await experienceApiRequest(form.dataset.detailUrl, "PATCH", payload);
        if (result.status !== 200 || result.data?.id !== form.dataset.experienceId) {
            throw new Error("Unexpected server response. Check the Experience list before trying again.");
        }
        // Show the saved representation, including text cleaned by the serializer.
        for (const name of Object.keys({ ...payload, display_order: result.data.display_order })) {
            const field = form.elements.namedItem(name);
            const value = result.data[name];
            if (name === "is_current") {
                if (field.type === "checkbox") field.checked = value === true;
                else field.value = value === true ? "true" : value === false ? "false" : "unknown";
            } else {
                field.value = value ?? "";
            }
        }
        const description = document.getElementById("edit-experience-description");
        if (description) description.textContent = `Update ${result.data.title} and its contributions.`;
        showToast("Success", "Experience successfully updated!", "success");
    } catch (error) {
        let message = error.message;
        if (error.status === 403) {
            message += " Your session may have expired or your permissions changed. Log in again or refresh before retrying.";
        } else if (error.status === 404) {
            message = "This Experience no longer exists. Return to the Experience list.";
        }
        showToast("Failed to update Experience", message, "error");
    } finally {
        // Failed requests leave every input available for correction or retry.
        submitButton.disabled = false;
    }
}

const editExperienceForm = document.getElementById("edit-experience-form");
if (editExperienceForm) editExperienceForm.addEventListener("submit", editExperience);

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

fetchExperiences(searchInput?.value.trim() || "");
window.addEventListener("pageshow", (event) => {
    // Browser Back can restore the list from memory after an edit.
    if (event.persisted && searchInput) refreshExperienceSearch();
});
