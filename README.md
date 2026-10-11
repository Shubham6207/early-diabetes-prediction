# Early Diabetes Prediction Website

Educational web app (**GlycoSight**) that estimates type 2 diabetes risk from eight routine clinical markers. Scoring runs entirely in the browser with a logistic regression model and a small threshold ensemble for comparison.

**GitHub:** [Shubham6207/early-diabetes-prediction](https://github.com/Shubham6207/early-diabetes-prediction)

This project is for learning and demonstration. It is **not** medical advice, diagnosis, or treatment.

## Features

- Interactive form for eight PIMA-style inputs: pregnancies, glucose, blood pressure, skin thickness, insulin, BMI, diabetes pedigree function, and age
- Logistic regression probability with a 50% decision threshold
- Second-opinion score from a compact clinical-threshold ensemble
- Ranked feature contributions so you can see what raised or lowered risk
- No backend, no accounts, and no uploads — values never leave your machine

## Project files

| File | Role |
| --- | --- |
| `index.html` | Page structure, form, and copy |
| `css/style.css` | Layout and styling |
| `js/model.js` | Risk models (logistic regression + ensemble) |
| `js/app.js` | Form handling and result display |
| `.gitignore` | Ignores OS junk files |

Those four web files are all that is required for the site to run. Fonts load from Google Fonts when you are online; the page still works offline without them.

## How to run

### Option 1 — Open the file

1. Clone or download this repository.
2. Open `index.html` in a modern browser (Chrome, Edge, or Firefox).

### Option 2 — Local web server (recommended)

From the project folder:

```bash
python -m http.server 8765
```

Then visit [http://127.0.0.1:8765/](http://127.0.0.1:8765/).

Enter marker values and click **Predict risk**, or use **Load high-risk sample** to see a canned demonstration profile (synthetic numbers, not a real patient).

## How the model works

1. Each input is standardized with PIMA-style training means and standard deviations.
2. Logistic regression computes `σ(w · x + b)` as the probability of the diabetes class.
3. A small set of glucose / BMI / age / pedigree threshold rules is shown as a second vote share.
4. Feature contributions (`weight × z-score`) are ranked in the result panel.

Glucose and BMI are typically the strongest drivers. The dataset lineage is the classic Pima Indians Diabetes teaching set, which is small and historically specific, so results are illustrative only.

## Privacy

- No API keys, passwords, or cloud services are used.
- No real patient records are stored in this repository.
- Form input stays in the browser session and is not written to disk or sent to a server.

## License / disclaimer

Use this code for education. If you are concerned about diabetes, speak with a qualified clinician and use standard tests (fasting glucose, HbA1c, or OGTT).
