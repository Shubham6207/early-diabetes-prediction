(function () {
  const form = document.getElementById("predict-form");
  const panel = document.getElementById("result-panel");
  const highSample = document.getElementById("sample-high");

  const HIGH_RISK_SAMPLE = {
    pregnancies: 8,
    glucose: 167,
    bloodPressure: 74,
    skinThickness: 32,
    insulin: 210,
    bmi: 38.2,
    dpf: 1.021,
    age: 51,
  };

  function readInputs(formEl) {
    const data = new FormData(formEl);
    return {
      pregnancies: data.get("pregnancies"),
      glucose: data.get("glucose"),
      bloodPressure: data.get("bloodPressure"),
      skinThickness: data.get("skinThickness"),
      insulin: data.get("insulin"),
      bmi: data.get("bmi"),
      dpf: data.get("dpf"),
      age: data.get("age"),
    };
  }

  function fillForm(values) {
    Object.entries(values).forEach(([name, value]) => {
      const field = form.elements.namedItem(name);
      if (field) field.value = value;
    });
  }

  function pct(value) {
    return `${Math.round(value * 100)}%`;
  }

  function gaugeSvg(probability) {
    const r = 46;
    const c = 2 * Math.PI * r;
    const offset = c * (1 - probability);
    return `
      <svg class="gauge-ring" viewBox="0 0 108 108" aria-hidden="true">
        <circle cx="54" cy="54" r="${r}" fill="none" stroke="#ebe4d6" stroke-width="10" />
        <circle cx="54" cy="54" r="${r}" fill="none" stroke="#0f5c4c" stroke-width="10"
          stroke-linecap="round" stroke-dasharray="${c.toFixed(1)}"
          stroke-dashoffset="${offset.toFixed(1)}"
          transform="rotate(-90 54 54)" />
      </svg>
    `;
  }

  function render(result) {
    const maxAbs = Math.max(
      ...result.logistic.contributions.map((item) => Math.abs(item.score)),
      0.001
    );
    const rows = result.logistic.contributions
      .slice(0, 6)
      .map((item) => {
        const width = Math.round((Math.abs(item.score) / maxAbs) * 100);
        const direction = item.score >= 0 ? "raises" : "lowers";
        return `
          <div class="contrib-row">
            <span>${item.label}</span>
            <div class="bar" title="${direction} risk"><span style="width:${width}%"></span></div>
            <span>${item.score >= 0 ? "+" : ""}${item.score.toFixed(2)}</span>
          </div>
        `;
      })
      .join("");

    panel.innerHTML = `
      <p class="eyebrow">Model output</p>
      <h3>
        <span class="risk-pill ${result.band.className}">${result.band.label}</span>
      </h3>
      <div class="gauge">
        ${gaugeSvg(result.logistic.probability)}
        <div>
          <p style="margin:0 0 0.2rem;font-size:1.8rem;font-family:var(--display);font-weight:650;">
            ${pct(result.logistic.probability)}
          </p>
          <p style="margin:0;color:var(--muted);">
            Logistic regression probability of the diabetes class
            (threshold 50%).
          </p>
        </div>
      </div>
      <p style="margin:0 0 0.4rem;font-weight:600;">Largest feature contributions</p>
      <div class="contrib">${rows}</div>
      <dl class="compare">
        <div>
          <dt>Logistic regression</dt>
          <dd>${pct(result.logistic.probability)}</dd>
        </div>
        <div>
          <dt>Threshold ensemble (${result.forest.votes}/${result.forest.trees} trees)</dt>
          <dd>${pct(result.forest.probability)}</dd>
        </div>
      </dl>
      <p style="margin:0.9rem 0 0;color:var(--muted);font-size:0.88rem;">
        Educational estimate only. Follow up with a clinician for testing.
      </p>
    `;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    render(DiabetesModel.predict(readInputs(form)));
  });

  form.addEventListener("reset", () => {
    window.setTimeout(() => {
      panel.innerHTML =
        '<p class="result-placeholder">Submit the form to see probability, risk band, and which features contributed most.</p>';
    }, 0);
  });

  highSample.addEventListener("click", () => {
    fillForm(HIGH_RISK_SAMPLE);
    render(DiabetesModel.predict(HIGH_RISK_SAMPLE));
  });
})();
