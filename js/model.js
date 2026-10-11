/**
 * Client-side diabetes risk models.
 *
 * Logistic regression uses standardized PIMA-style statistics and
 * coefficients typical of a well-fit sklearn LogisticRegression.
 * The second model is a small ensemble of clinical threshold trees
 * (a transparent stand-in for a random forest) for comparison.
 */
const DiabetesModel = (() => {
  const FEATURES = [
    {
      key: "pregnancies",
      label: "Pregnancies",
      mean: 3.845,
      std: 3.37,
      weight: 0.408,
    },
    {
      key: "glucose",
      label: "Glucose",
      mean: 120.895,
      std: 31.973,
      weight: 1.128,
    },
    {
      key: "bloodPressure",
      label: "Blood pressure",
      mean: 69.105,
      std: 19.356,
      weight: -0.257,
    },
    {
      key: "skinThickness",
      label: "Skin thickness",
      mean: 20.537,
      std: 15.952,
      weight: 0.047,
    },
    {
      key: "insulin",
      label: "Insulin",
      mean: 79.799,
      std: 115.244,
      weight: -0.137,
    },
    {
      key: "bmi",
      label: "BMI",
      mean: 31.993,
      std: 7.884,
      weight: 0.621,
    },
    {
      key: "dpf",
      label: "Pedigree",
      mean: 0.472,
      std: 0.331,
      weight: 0.309,
    },
    {
      key: "age",
      label: "Age",
      mean: 33.241,
      std: 11.76,
      weight: 0.178,
    },
  ];

  const INTERCEPT = -0.841;

  function sigmoid(z) {
    if (z >= 0) {
      const ez = Math.exp(-z);
      return 1 / (1 + ez);
    }
    const ez = Math.exp(z);
    return ez / (1 + ez);
  }

  function zscore(feature, value) {
    return (Number(value) - feature.mean) / feature.std;
  }

  function logisticRegression(inputs) {
    const contributions = FEATURES.map((feature) => {
      const z = zscore(feature, inputs[feature.key]);
      const score = feature.weight * z;
      return { ...feature, z, score };
    });
    const logit =
      INTERCEPT + contributions.reduce((sum, item) => sum + item.score, 0);
    const probability = sigmoid(logit);
    contributions.sort((a, b) => Math.abs(b.score) - Math.abs(a.score));
    return { probability, logit, contributions };
  }

  function treeVote(inputs) {
    const g = Number(inputs.glucose);
    const bmi = Number(inputs.bmi);
    const age = Number(inputs.age);
    const dpf = Number(inputs.dpf);
    const preg = Number(inputs.pregnancies);
    const insulin = Number(inputs.insulin);

    const trees = [
      g > 154 ? 1 : g > 126 && bmi >= 30 ? 1 : 0,
      bmi >= 35 && age >= 40 ? 1 : bmi >= 30 && g > 110 ? 1 : 0,
      dpf >= 0.8 && g > 120 ? 1 : age >= 50 && g > 100 ? 1 : 0,
      preg >= 6 && g > 115 ? 1 : insulin > 180 && bmi >= 32 ? 1 : 0,
      g > 140 ? 1 : g > 100 && age >= 45 && bmi >= 28 ? 1 : 0,
    ];
    const votes = trees.reduce((sum, vote) => sum + vote, 0);
    return { probability: votes / trees.length, votes, trees: trees.length };
  }

  function riskBand(probability) {
    if (probability < 0.35) {
      return { label: "Lower estimated risk", className: "risk-low" };
    }
    if (probability < 0.55) {
      return { label: "Moderate estimated risk", className: "risk-moderate" };
    }
    return { label: "Higher estimated risk", className: "risk-high" };
  }

  function predict(inputs) {
    const lr = logisticRegression(inputs);
    const forest = treeVote(inputs);
    return {
      logistic: lr,
      forest,
      band: riskBand(lr.probability),
    };
  }

  return { FEATURES, predict };
})();
