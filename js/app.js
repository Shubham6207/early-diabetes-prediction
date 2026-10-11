(function () {
  const form = document.getElementById("predict-form");
  const panel = document.getElementById("result-panel");
  const highSample = document.getElementById("sample-high");

  // Set this to the deployed Flask API URL, for example:
  // window.DIABETES_API_URL = "https://your-service.onrender.com";
  const API_BASE_URL = (window.DIABETES_API_URL || "").replace(/\/$/, "");

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
      pregnancies: Number(data.get("pregnancies")),
      glucose: Number(data.get("glucose")),
      bloodPressure: Number(data.get("bloodPressure")),
      skinThickness: Number(data.get("skinThickness")),
      insulin: Number(data.get("insulin")),
      bmi: Number(data.get("bmi")),
      dpf: Number(data.get("dpf")),
      age: Number(data.get("age")),
    };
  }

  function toApiPayload(inputs) {
    return {
      Pregnancies: inputs.pregnancies,
      Glucose: inputs.glucose,
      BloodPressure: inputs.bloodPressure,
      SkinThickness: inputs.skinThickness,
      Insulin: inputs.insulin,
      BMI: inputs.bmi,
      DiabetesPedigreeFunction: inputs.dpf,
      Age: inputs.age,
    };
  }

  function showMessage(message, isError = false) {
    panel.innerHTML = "";
    const p = document.createElement("p");
    p.className = isError ? "result-error" : "result-placeholder";
    p.textContent = message;
    panel.appendChild(p);
  }

  function render(result) {
    const probability = Math.max(0, Math.min(100, Number(result.probability)));
    const positive = Number(result.prediction) === 1;
    const label = positive ? "Higher model estimate" : "Lower model estimate";
    const className = positive ? "risk-high" : "risk-low";

    panel.innerHTML = `
      <p class="eyebrow">Python ML model output</p>
      <h3><span class="risk-pill ${className}">${label}</span></h3>
      <div class="gauge">
        <div class="gauge-ring" style="display:grid;place-items:center;width:108px;height:108px;border-radius:50%;border:10px solid #ebe4d6;box-sizing:border-box;">
          <span style="font-size:1.1rem;font-weight:700;">${probability.toFixed(1)}%</span>
        </div>
        <div>
          <p style="margin:0 0 0.2rem;font-size:1.8rem;font-family:var(--display);font-weight:650;">${probability.toFixed(1)}%</p>
          <p style="margin:0;color:var(--muted);">Model-estimated probability for the positive class.</p>
        </div>
      </div>
      <p style="margin:0.8rem 0 0;color:var(--muted);font-size:0.88rem;">
        ${result.disclaimer || "Educational estimate only; not a medical diagnosis."}
      </p>
    `;
  }

  async function predict(inputs) {
    if (!API_BASE_URL) {
      showMessage("Backend URL is not configured yet. Deploy the Flask API, then set window.DIABETES_API_URL to its public URL.", true);
      return;
    }

    showMessage("Python ML model se prediction li ja rahi hai...");
    try {
      const response = await fetch(`${API_BASE_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(toApiPayload(inputs)),
      });
      const result = await response.json();
      if (!response.ok || !result.success) {
        throw new Error(result.error || "Prediction request failed.");
      }
      render(result);
    } catch (error) {
      showMessage(`Prediction nahi ho payi: ${error.message}. Backend URL aur deployment status check karo.`, true);
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    predict(readInputs(form));
  });

  form.addEventListener("reset", () => {
    window.setTimeout(() => {
      showMessage("Submit the form to get a prediction from the Python ML model.");
    }, 0);
  });

  highSample.addEventListener("click", () => {
    Object.entries(HIGH_RISK_SAMPLE).forEach(([name, value]) => {
      const field = form.elements.namedItem(name);
      if (field) field.value = value;
    });
    predict(HIGH_RISK_SAMPLE);
  });
})();
