const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { test } = require("node:test");

const source = fs.readFileSync(path.join(__dirname, "../static/js/experience.js"), "utf8");
const id = "11111111-2222-4333-8444-555555555555";

function setup(reply) {
    const values = {
        title: "<b>New title</b>", description: "<p>Saved text</p>", category: "research",
        organization: "<b>Studio</b>", logo_static_path: "", logo_alt: "<i>Logo</i>",
        start_year: "2025", start_month: "", end_year: "", end_month: "",
        display_order: "", is_current: "unknown",
    };
    const fields = Object.fromEntries(Object.entries(values).map(([name, value]) =>
        [name, { value, type: name === "is_current" ? "select-one" : "text" }]));
    const button = { disabled: false };
    const form = {
        dataset: { detailUrl: `/api/v1/experiences/${id}/`, experienceId: id },
        elements: { namedItem: name => fields[name] }, querySelector: () => button,
        addEventListener: (name, handler) => { form.submit = handler; },
    };
    const description = { textContent: "Update Old title and its contributions." };
    const calls = [], toasts = [];
    const context = {
        document: { cookie: "csrftoken=test-token", getElementById: name =>
            name === "edit-experience-form" ? form : name === "edit-experience-description" ? description : null },
        window: { addEventListener() {} },
        fetch: async (...args) => { calls.push(args); return reply(); },
        showToast: (...args) => toasts.push(args), setTimeout, clearTimeout,
    };
    vm.runInNewContext(source, context);
    const submit = () => {
        let prevented = false;
        const result = form.submit({ currentTarget: form, preventDefault() { prevented = true; } });
        assert(prevented);
        return result;
    };
    return { fields, button, description, calls, toasts, submit };
}

const response = (status, data) => ({ status, ok: status < 400, json: async () => data });

test("PATCH refreshes the form and heading from the saved, sanitized representation", async () => {
    for (const current of [null, false, true]) {
        const saved = { id, title: "New title", description: "Saved text", category: "research",
            organization: "Studio", logo_static_path: "", logo_alt: "Logo", start_year: 2025,
            start_month: null, end_year: null, end_month: null, is_current: current, display_order: 4 };
        const state = setup(() => response(200, saved));
        await state.submit();
        for (const name of ["title", "description", "organization", "logo_alt", "display_order"])
            assert.equal(state.fields[name].value, saved[name]);
        for (const name of ["start_month", "end_year", "end_month"]) assert.equal(state.fields[name].value, "");
        assert.equal(state.fields.is_current.value, current === null ? "unknown" : String(current));
        assert.equal(state.description.textContent, "Update New title and its contributions.");
        assert.equal(state.toasts[0][2], "success");
        assert.equal(state.calls[0][0], `/api/v1/experiences/${id}/`);
        const options = state.calls[0][1];
        assert.equal(options.method, "PATCH");
        assert.equal(options.credentials, "same-origin");
        assert.equal(options.headers["X-CSRFToken"], "test-token");
        assert.equal(options.headers["Content-Type"], "application/json");
        assert.equal(state.button.disabled, false);
    }
});

test("rejected, missing, network, and unexpected responses preserve unsaved inputs", async () => {
    for (const reply of [
        () => response(400, { title: ["Invalid <input>"] }),
        () => response(403, { detail: "Forbidden" }),
        () => response(404, { detail: "Not found" }),
        () => { throw new Error("offline"); },
        () => response(200, { id: "wrong-record" }),
    ]) {
        const state = setup(reply);
        const before = JSON.stringify(state.fields);
        await state.submit();
        assert.equal(JSON.stringify(state.fields), before);
        assert.equal(state.description.textContent, "Update Old title and its contributions.");
        assert.equal(state.toasts[0][2], "error");
        assert.equal(state.button.disabled, false);
    }
});
