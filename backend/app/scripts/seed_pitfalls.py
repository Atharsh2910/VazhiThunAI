"""
Seed script: populate pitfall knowledge base.

Run from the backend/ directory:
    python -m app.scripts.seed_pitfalls

Creates: Concepts, Pitfalls, PitfallQuestions, PitfallOptionMappings
Skips existing rows (idempotent).
"""
import sys
import os

# Allow running as a module from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from app.models.database import SessionLocal, engine, Base
from app.models.orm import (
    Concept, Pitfall, PitfallQuestion, PitfallOptionMapping
)

# Create all tables (including the new pitfall ones)
Base.metadata.create_all(bind=engine)

# ─────────────────────────────────────────────
# Seed Data Definition
# ─────────────────────────────────────────────

SEED_DATA = [
    # ─── STATISTICS ───────────────────────────────────────────────
    {
        "concept_id": "CON_COND_PROB",
        "skill_id": "SK017",   # Inferential Statistics
        "name": "Conditional Probability",
        "description": "The probability of an event given that another event has occurred.",
        "pitfalls": [
            {
                "pitfall_id": "PF001",
                "title": "Confusing P(A|B) with P(B|A)",
                "description": "Learners swap the conditioning direction in probability statements.",
                "misconception": "P(A|B) equals P(B|A) because they both involve the same two events.",
                "correct_mental_model": "P(A|B) = P(A and B) / P(B). Flipping the condition changes the denominator and gives a completely different value. This confusion is the root of the 'Prosecutor's Fallacy'.",
                "severity": "high",
                "remediation_text": "P(disease | positive test) is NOT the same as P(positive test | disease). The denominator changes. Always identify which event you are conditioning ON.",
                "questions": [
                    {
                        "question_id": "PFQ001",
                        "question_text": "A disease affects 1% of the population. A test for it is 95% accurate. A patient tests positive. A doctor says 'The test is 95% accurate, so there is a 95% chance the patient has the disease.' Is the doctor correct?",
                        "options": {
                            "A": "Yes — the 95% accuracy directly gives the probability of having the disease.",
                            "B": "No — the probability of having the disease given a positive test also depends on the base rate (prevalence) of the disease.",
                            "C": "Yes — the patient tested positive, so the accuracy applies directly.",
                            "D": "No — because no medical test can be 95% accurate."
                        },
                        "correct_option": "B",
                        "explanation": "This is the base-rate fallacy. P(disease | positive) depends on P(disease) via Bayes' theorem. With 1% prevalence, the actual probability is much lower than 95%.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Confuses P(positive|disease) with P(disease|positive) — the classic direction-swap error."},
                            {"option_key": "C", "misconception_hint": "Same as A — ignores the base rate and reverses the conditioning direction."},
                            {"option_key": "D", "misconception_hint": "Irrelevant distractor about test quality, avoids the real probability reasoning."}
                        ]
                    },
                    {
                        "question_id": "PFQ002",
                        "question_text": "In a class, 60% of students who pass the exam studied hard. What is the probability that a student who studied hard will pass?",
                        "options": {
                            "A": "60%",
                            "B": "Cannot be determined from the given information alone.",
                            "C": "40%",
                            "D": "100%, because studying hard guarantees passing."
                        },
                        "correct_option": "B",
                        "explanation": "We are given P(studied hard | passed) = 60%. To find P(passed | studied hard) we need P(passed) and P(studied hard) as well. They are not the same value.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Assumes P(studied|passed) = P(passed|studied) — the classic conditional probability reversal."},
                            {"option_key": "C", "misconception_hint": "Takes the complement of a misread probability — compounds the direction-swap error."},
                            {"option_key": "D", "misconception_hint": "Causal reasoning error — equates studying with certainty of passing."}
                        ]
                    }
                ]
            },
            {
                "pitfall_id": "PF002",
                "title": "Correlation implies Causation",
                "description": "Learners incorrectly conclude that a statistical correlation between two variables means one causes the other.",
                "misconception": "If two variables are correlated, one must cause the other.",
                "correct_mental_model": "Correlation measures the strength and direction of a linear relationship. Causation requires controlled experiments, temporal precedence, and ruling out confounding variables. A third variable (confounder) often explains both.",
                "severity": "high",
                "remediation_text": "Ice cream sales correlate with drowning rates — neither causes the other. Both are caused by hot weather (a confounder). Correlation ≠ causation.",
                "questions": [
                    {
                        "question_id": "PFQ003",
                        "question_text": "A study finds a strong positive correlation (r = 0.85) between shoe size and reading ability in children. Which conclusion is MOST appropriate?",
                        "options": {
                            "A": "Larger shoe size causes better reading ability.",
                            "B": "Better reading ability causes larger shoe sizes.",
                            "C": "A third variable, such as age, likely explains both — older children have bigger feet and read better.",
                            "D": "The finding is meaningless because shoe size and reading are unrelated."
                        },
                        "correct_option": "C",
                        "explanation": "Age is a confounding variable. As children age, both shoe size and reading ability increase. The correlation is spurious.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Classic causal arrow error from correlation — ignores the confounding variable."},
                            {"option_key": "B", "misconception_hint": "Reverses the causal arrow — still the same fundamental correlation-causation confusion."},
                            {"option_key": "D", "misconception_hint": "Dismisses a real correlation without considering confounders — correlation is real, causal interpretation is wrong."}
                        ]
                    },
                    {
                        "question_id": "PFQ004",
                        "question_text": "Which of the following provides the STRONGEST evidence of causation (not just correlation)?",
                        "options": {
                            "A": "A large observational dataset showing r = 0.95 between two variables.",
                            "B": "A randomized controlled experiment where only the treatment variable is changed and outcomes are measured.",
                            "C": "A time-series showing variable A consistently increases before variable B.",
                            "D": "A peer-reviewed observational study with thousands of participants."
                        },
                        "correct_option": "B",
                        "explanation": "Random assignment isolates the causal effect by controlling confounding variables. Observational studies, no matter how large, cannot rule out confounders.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "High correlation is not causation — even r=0.99 can be spurious."},
                            {"option_key": "C", "misconception_hint": "Temporal precedence is one criterion but not sufficient for causation on its own."},
                            {"option_key": "D", "misconception_hint": "Large sample size strengthens statistical power but doesn't eliminate confounding in observational designs."}
                        ]
                    }
                ]
            }
        ]
    },
    # ─── MACHINE LEARNING ─────────────────────────────────────────
    {
        "concept_id": "CON_DATA_LEAKAGE",
        "skill_id": "SK021",   # ML Foundations
        "name": "Data Leakage",
        "description": "When information from outside the training dataset is used to train the model, causing overly optimistic evaluation.",
        "pitfalls": [
            {
                "pitfall_id": "PF003",
                "title": "Scaling before splitting causes leakage",
                "description": "Learners apply StandardScaler or MinMaxScaler on the full dataset before train/test split.",
                "misconception": "It is fine to scale the entire dataset before splitting because scaling is just a transformation, not learning from data.",
                "correct_mental_model": "Scaling parameters (mean, std) computed on the full dataset include test-set information. The scaler must be fit ONLY on the training set, then used to transform both train and test sets.",
                "severity": "high",
                "remediation_text": "Always: split first → fit scaler on train → transform train and test. Never fit on the combined dataset.",
                "questions": [
                    {
                        "question_id": "PFQ005",
                        "question_text": "A data scientist runs StandardScaler().fit_transform(X) on the full dataset, then does train_test_split. What is the main problem?",
                        "options": {
                            "A": "StandardScaler is only for classification, not regression.",
                            "B": "The scaler's mean and standard deviation are computed using test data, leaking test information into the training process.",
                            "C": "fit_transform is slower than fit followed by transform.",
                            "D": "There is no problem — scaling before splitting is the recommended approach."
                        },
                        "correct_option": "B",
                        "explanation": "The scaler learns statistics (mean, std) from the test set, allowing test-set information to influence training — this is data leakage.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Confuses the algorithm's applicability with the leakage problem — unrelated to scaling type."},
                            {"option_key": "C", "misconception_hint": "Performance concern, not a correctness concern — completely misses the leakage issue."},
                            {"option_key": "D", "misconception_hint": "Directly exhibits the misconception: believes pre-split scaling is correct."}
                        ]
                    },
                    {
                        "question_id": "PFQ006",
                        "question_text": "Which of the following correctly avoids data leakage when preprocessing?",
                        "options": {
                            "A": "Apply scaling on X_train and X_test separately using fit_transform on each.",
                            "B": "Split first, then fit the scaler on X_train, then transform both X_train and X_test using the same scaler.",
                            "C": "Apply scaling on all data before splitting, then split.",
                            "D": "Use cross-validation instead of train/test split — this automatically prevents leakage."
                        },
                        "correct_option": "B",
                        "explanation": "Fitting the scaler only on X_train ensures no test information contaminates the preprocessing step.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Fitting separately on test set introduces inconsistency — test gets different scale than training."},
                            {"option_key": "C", "misconception_hint": "Classic leakage pattern — fitting on full data before splitting."},
                            {"option_key": "D", "misconception_hint": "Cross-validation can also suffer leakage if preprocessing is done outside the CV loop."}
                        ]
                    }
                ]
            }
        ]
    },
    {
        "concept_id": "CON_OVERFITTING",
        "skill_id": "SK021",   # ML Foundations
        "name": "Overfitting vs Generalization",
        "description": "Overfitting is when a model memorizes training data instead of learning generalizable patterns.",
        "pitfalls": [
            {
                "pitfall_id": "PF004",
                "title": "Training accuracy as generalization proxy",
                "description": "Learners equate high training accuracy with a good model.",
                "misconception": "If the model achieves 99% accuracy on the training data, it is a great model.",
                "correct_mental_model": "Training accuracy measures memorization, not generalization. A model with 99% train accuracy and 60% test accuracy has severely overfit — it performs poorly on unseen data.",
                "severity": "high",
                "remediation_text": "Always evaluate on a held-out test set that the model has never seen. High train accuracy + low test accuracy = overfitting.",
                "questions": [
                    {
                        "question_id": "PFQ007",
                        "question_text": "A decision tree achieves 99% accuracy on training data and 61% accuracy on test data. What does this indicate?",
                        "options": {
                            "A": "The model is excellent — 99% accuracy is very high.",
                            "B": "The model has overfit the training data and will not generalize well.",
                            "C": "The test set must contain errors — the model is correct.",
                            "D": "The model is underfitting — it needs more complexity."
                        },
                        "correct_option": "B",
                        "explanation": "The large gap between train accuracy (99%) and test accuracy (61%) is the signature of overfitting — the model memorized training patterns but fails on new data.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Directly exhibits the misconception: judging model quality solely on training accuracy."},
                            {"option_key": "C", "misconception_hint": "Rationalizes overfitting by blaming the test data rather than recognizing the generalization gap."},
                            {"option_key": "D", "misconception_hint": "Confuses the direction — underfitting shows LOW train accuracy, not high. 99% train = overfitting, not underfitting."}
                        ]
                    },
                    {
                        "question_id": "PFQ008",
                        "question_text": "Which technique directly addresses overfitting by penalizing model complexity?",
                        "options": {
                            "A": "Increasing training set size only.",
                            "B": "Using regularization (L1 or L2 penalty).",
                            "C": "Removing the test set and using all data for training.",
                            "D": "Using a more complex model architecture."
                        },
                        "correct_option": "B",
                        "explanation": "L1/L2 regularization adds a penalty term to the loss function that discourages large coefficients, reducing the model's tendency to overfit.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "More data helps but alone may not prevent overfitting if the model is too complex."},
                            {"option_key": "C", "misconception_hint": "Removing evaluation completely eliminates the ability to detect overfitting at all."},
                            {"option_key": "D", "misconception_hint": "Increasing complexity makes overfitting worse, not better."}
                        ]
                    }
                ]
            }
        ]
    },
    # ─── PYTHON ───────────────────────────────────────────────────
    {
        "concept_id": "CON_MUTABLE_DEFAULTS",
        "skill_id": "SK001",   # Python Basics
        "name": "Mutable Default Arguments",
        "description": "Using mutable objects (lists, dicts) as default argument values in Python functions.",
        "pitfalls": [
            {
                "pitfall_id": "PF005",
                "title": "Mutable default argument is shared across calls",
                "description": "Learners expect a fresh list/dict on each function call when using a mutable default argument.",
                "misconception": "def f(items=[]): items.append(1) creates a fresh empty list for each call.",
                "correct_mental_model": "Default argument values are evaluated ONCE when the function is defined. The same mutable object is shared across all calls. Use None as default and create a new object inside the function body.",
                "severity": "medium",
                "remediation_text": "Use: def f(items=None): if items is None: items = []. This creates a new list on each call.",
                "questions": [
                    {
                        "question_id": "PFQ009",
                        "question_text": "What does the following code print?\n\ndef append_to(element, to=[]):\n    to.append(element)\n    return to\n\nprint(append_to(1))\nprint(append_to(2))",
                        "options": {
                            "A": "[1]\n[2]",
                            "B": "[1]\n[1, 2]",
                            "C": "Error: cannot append to a default argument.",
                            "D": "[1, 2]\n[1, 2]"
                        },
                        "correct_option": "B",
                        "explanation": "The default list `to=[]` is created once when the function is defined. Each call without an explicit `to` argument shares the same list object, accumulating values.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Assumes a fresh list is created on each call — the core mutable default argument misconception."},
                            {"option_key": "C", "misconception_hint": "No error occurs — Python happily mutates the shared default object."},
                            {"option_key": "D", "misconception_hint": "The first call returns [1] not [1,2] — partially correct for the second call but wrong for the first."}
                        ]
                    },
                    {
                        "question_id": "PFQ010",
                        "question_text": "What is the CORRECT way to write a function that takes an optional list and does not share state between calls?",
                        "options": {
                            "A": "def f(items=[]): pass",
                            "B": "def f(items=list()): pass",
                            "C": "def f(items=None):\n    if items is None:\n        items = []\n    pass",
                            "D": "def f(items=()): pass  # use a tuple instead"
                        },
                        "correct_option": "C",
                        "explanation": "Using None as the sentinel and creating a new list inside the function ensures each call gets a fresh object.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Exact mutable default anti-pattern — shared across calls."},
                            {"option_key": "B", "misconception_hint": "list() is evaluated once at definition time, same issue as []"},
                            {"option_key": "D", "misconception_hint": "Tuples are immutable so cannot be accidentally mutated, but the caller still can't add to it — not equivalent."}
                        ]
                    }
                ]
            }
        ]
    },
    # ─── SQL ──────────────────────────────────────────────────────
    {
        "concept_id": "CON_WHERE_HAVING",
        "skill_id": "SK012",   # SQL Basics
        "name": "WHERE vs HAVING",
        "description": "WHERE filters rows before grouping; HAVING filters groups after aggregation.",
        "pitfalls": [
            {
                "pitfall_id": "PF006",
                "title": "Using WHERE to filter aggregated values",
                "description": "Learners try to use WHERE with aggregate functions like COUNT, SUM, AVG.",
                "misconception": "WHERE can be used to filter based on aggregate function results like WHERE COUNT(*) > 5.",
                "correct_mental_model": "WHERE is applied before GROUP BY and cannot reference aggregate functions. HAVING is applied after GROUP BY and CAN reference aggregates.",
                "severity": "medium",
                "remediation_text": "Rule: filter RAW column values → WHERE. Filter AGGREGATED values → HAVING.",
                "questions": [
                    {
                        "question_id": "PFQ011",
                        "question_text": "You want to find departments with more than 10 employees. Which query is correct?",
                        "options": {
                            "A": "SELECT department, COUNT(*) FROM employees WHERE COUNT(*) > 10 GROUP BY department;",
                            "B": "SELECT department, COUNT(*) FROM employees GROUP BY department HAVING COUNT(*) > 10;",
                            "C": "SELECT department, COUNT(*) FROM employees HAVING COUNT(*) > 10;",
                            "D": "SELECT department, COUNT(*) FROM employees GROUP BY department WHERE COUNT(*) > 10;"
                        },
                        "correct_option": "B",
                        "explanation": "HAVING filters after GROUP BY. WHERE cannot use aggregate functions and must come before GROUP BY.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Uses WHERE with an aggregate — the classic WHERE vs HAVING confusion. This query will raise an error."},
                            {"option_key": "C", "misconception_hint": "Missing GROUP BY — HAVING without GROUP BY is valid in some databases but semantically wrong here."},
                            {"option_key": "D", "misconception_hint": "WHERE placed after GROUP BY — syntactically invalid in SQL."}
                        ]
                    },
                    {
                        "question_id": "PFQ012",
                        "question_text": "Which clause is evaluated FIRST in a SQL query with both WHERE and HAVING?",
                        "options": {
                            "A": "HAVING — because it filters the final result.",
                            "B": "WHERE — because it filters raw rows before grouping.",
                            "C": "Both are evaluated simultaneously.",
                            "D": "It depends on the database engine."
                        },
                        "correct_option": "B",
                        "explanation": "SQL logical order: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY. WHERE always runs before GROUP BY and HAVING.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Reverses the execution order — HAVING comes after WHERE in the SQL logical processing order."},
                            {"option_key": "C", "misconception_hint": "They are never simultaneous — SQL has a well-defined logical evaluation order."},
                            {"option_key": "D", "misconception_hint": "While physical execution may vary, the logical order is defined by SQL standard."}
                        ]
                    }
                ]
            }
        ]
    },
    # ─── DEEP LEARNING ────────────────────────────────────────────
    {
        "concept_id": "CON_ACTIVATION",
        "skill_id": "SK021",   # ML Foundations (closest match)
        "name": "Activation Functions",
        "description": "Non-linear functions applied at each neuron that allow neural networks to learn complex patterns.",
        "pitfalls": [
            {
                "pitfall_id": "PF007",
                "title": "Sigmoid causes vanishing gradients in deep networks",
                "description": "Learners use sigmoid in hidden layers of deep networks without realizing it causes vanishing gradients.",
                "misconception": "Sigmoid is a good default activation function for all layers in a deep neural network because it squashes values between 0 and 1.",
                "correct_mental_model": "Sigmoid's gradient is at most 0.25. When backpropagating through many layers, gradients are multiplied repeatedly and become exponentially small — making early layers learn very slowly or not at all. ReLU is preferred for hidden layers.",
                "severity": "medium",
                "remediation_text": "Use ReLU (or variants) for hidden layers. Reserve sigmoid for binary output layers where you need probability output.",
                "questions": [
                    {
                        "question_id": "PFQ013",
                        "question_text": "Why is sigmoid activation generally avoided in hidden layers of deep networks?",
                        "options": {
                            "A": "Sigmoid is computationally too expensive compared to ReLU.",
                            "B": "Sigmoid outputs are always negative, which confuses the optimizer.",
                            "C": "Sigmoid gradients saturate near 0 and 1, causing vanishing gradients during backpropagation through many layers.",
                            "D": "Sigmoid cannot be used in multi-class problems."
                        },
                        "correct_option": "C",
                        "explanation": "The sigmoid derivative is ≤ 0.25. Multiplied across many layers during backprop, gradients shrink exponentially — the vanishing gradient problem.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Computation cost is marginal and not the primary reason — focuses on wrong attribute."},
                            {"option_key": "B", "misconception_hint": "Sigmoid outputs are between 0 and 1 (positive), not negative — factual misconception."},
                            {"option_key": "D", "misconception_hint": "Multi-class uses softmax at the output; sigmoid in hidden layers is unrelated to this."}
                        ]
                    },
                    {
                        "question_id": "PFQ014",
                        "question_text": "A network has 10 hidden layers, all using sigmoid activation. Training loss barely decreases after many epochs. What is the MOST likely cause?",
                        "options": {
                            "A": "The learning rate is too high.",
                            "B": "The network has too many layers for the dataset.",
                            "C": "Vanishing gradients — sigmoid saturates, causing gradients to become near-zero in early layers.",
                            "D": "The model is underfitting because sigmoid limits output range."
                        },
                        "correct_option": "C",
                        "explanation": "10 layers of sigmoid means gradients are multiplied by ≤0.25 ten times — resulting in gradients of ≤0.25^10 ≈ 0.000001, making early layer learning effectively zero.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "High LR causes instability/oscillation not stagnation; plausible but not MOST likely given the architecture clue."},
                            {"option_key": "B", "misconception_hint": "Too many layers is the context but doesn't name the mechanism — vanishing gradients is the precise cause."},
                            {"option_key": "D", "misconception_hint": "Confuses output range limitation with gradient flow — the problem is gradient, not output scale."}
                        ]
                    }
                ]
            }
        ]
    },
    # ─── MODEL EVALUATION ─────────────────────────────────────────
    {
        "concept_id": "CON_ACCURACY_IMBALANCE",
        "skill_id": "SK024",   # Model Evaluation
        "name": "Accuracy on Imbalanced Datasets",
        "description": "Accuracy is misleading when class distribution is heavily skewed.",
        "pitfalls": [
            {
                "pitfall_id": "PF008",
                "title": "High accuracy on imbalanced data is misleading",
                "description": "Learners accept high accuracy as evidence of a good model even when the dataset is imbalanced.",
                "misconception": "95% accuracy always means a model is performing well.",
                "correct_mental_model": "On a dataset where 95% of samples are class A, a model that always predicts class A achieves 95% accuracy without learning anything. Use F1-score, precision/recall, or AUC-ROC for imbalanced problems.",
                "severity": "high",
                "remediation_text": "For imbalanced data: check the class distribution first. A classifier that always predicts the majority class can achieve high accuracy. Use recall, precision, F1, or confusion matrix instead.",
                "questions": [
                    {
                        "question_id": "PFQ015",
                        "question_text": "A fraud detection model reports 99% accuracy. The dataset has 99% non-fraud and 1% fraud transactions. What can we conclude?",
                        "options": {
                            "A": "The model is excellent at detecting fraud.",
                            "B": "The accuracy metric is misleading — the model may simply always predict 'non-fraud'.",
                            "C": "The model is perfect — 99% accuracy matches the dataset distribution.",
                            "D": "We need more data to evaluate the model."
                        },
                        "correct_option": "B",
                        "explanation": "A trivial model that always predicts 'non-fraud' achieves 99% accuracy but has 0% recall for fraud — completely useless for its purpose.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Accepts accuracy at face value without considering class imbalance — the core misconception."},
                            {"option_key": "C", "misconception_hint": "The 'match' is coincidental — it proves the model learned nothing, not that it's perfect."},
                            {"option_key": "D", "misconception_hint": "More data isn't the issue — the evaluation metric is wrong for this problem."}
                        ]
                    },
                    {
                        "question_id": "PFQ016",
                        "question_text": "Which metric is MOST appropriate for evaluating a binary classifier on a highly imbalanced dataset?",
                        "options": {
                            "A": "Accuracy",
                            "B": "Mean Squared Error",
                            "C": "F1-Score or AUC-ROC",
                            "D": "R-squared"
                        },
                        "correct_option": "C",
                        "explanation": "F1-score balances precision and recall. AUC-ROC measures the trade-off across all thresholds. Both are robust to class imbalance unlike raw accuracy.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Accuracy is unreliable for imbalanced data — the misconception the question targets."},
                            {"option_key": "B", "misconception_hint": "MSE is a regression metric — not applicable to binary classification."},
                            {"option_key": "D", "misconception_hint": "R-squared is also a regression metric — not applicable to binary classification."}
                        ]
                    }
                ]
            }
        ]
    },
    # ─── DESCRIPTIVE STATISTICS ───────────────────────────────────
    {
        "concept_id": "CON_MEAN_OUTLIER",
        "skill_id": "SK011",   # Descriptive Statistics
        "name": "Mean vs Median with Outliers",
        "description": "The mean is sensitive to outliers while the median is robust.",
        "pitfalls": [
            {
                "pitfall_id": "PF009",
                "title": "Mean always represents the typical value",
                "description": "Learners assume the mean is always the best measure of central tendency.",
                "misconception": "The mean is always the best way to describe the center of a dataset.",
                "correct_mental_model": "The mean is heavily influenced by outliers. In skewed distributions (income, house prices), the median better represents the typical value. The mean can be pulled far from where most values cluster.",
                "severity": "low",
                "remediation_text": "For skewed data or data with outliers, use the median. Example: 5 people earn $30k/year, 1 earns $1M. Mean = $197k (unrepresentative). Median = $30k (representative).",
                "questions": [
                    {
                        "question_id": "PFQ017",
                        "question_text": "Five employees earn $30,000 per year. The CEO earns $1,000,000. What is the MOST representative measure of central tendency for this salary dataset?",
                        "options": {
                            "A": "Mean — it uses all data points and is mathematically precise.",
                            "B": "Median — it is resistant to the outlier (CEO salary) and better represents typical earnings.",
                            "C": "Mode — the most frequent value is most representative.",
                            "D": "Standard deviation — it captures the spread of salaries."
                        },
                        "correct_option": "B",
                        "explanation": "The CEO's salary pulls the mean to ~$197k, far above what most employees earn. The median ($30k) correctly represents the typical salary.",
                        "option_mappings": [
                            {"option_key": "A", "misconception_hint": "Precision ≠ representativeness. The mean is precise but misleading here — the core misconception."},
                            {"option_key": "C", "misconception_hint": "Mode is the most frequent value — useful for categorical data, less so for continuous salary data here."},
                            {"option_key": "D", "misconception_hint": "Standard deviation is a measure of spread, not central tendency."}
                        ]
                    },
                    {
                        "question_id": "PFQ018",
                        "question_text": "A dataset of house prices has a few extremely expensive mansions. The distribution is right-skewed. Which is TRUE?",
                        "options": {
                            "A": "Mean > Median (outliers pull the mean right).",
                            "B": "Mean < Median (outliers pull the mean left).",
                            "C": "Mean = Median (skewness doesn't affect the mean).",
                            "D": "Median > Mode always in right-skewed distributions."
                        },
                        "correct_option": "A",
                        "explanation": "In right-skewed distributions, the long tail on the right pulls the mean above the median. A useful rule: right-skewed → mean > median > mode.",
                        "option_mappings": [
                            {"option_key": "B", "misconception_hint": "Confuses right-skew direction — right tail pulls mean RIGHT (higher), not left."},
                            {"option_key": "C", "misconception_hint": "Skewness absolutely affects the mean — it's the defining characteristic of skewed distributions."},
                            {"option_key": "D", "misconception_hint": "While often true, 'always' is too strong and not the core issue — also median vs mode is not the main relationship here."}
                        ]
                    }
                ]
            }
        ]
    }
]


def seed(db):
    created_concepts = 0
    created_pitfalls = 0
    created_questions = 0
    created_mappings = 0

    for concept_data in SEED_DATA:
        # Upsert Concept
        concept = db.query(Concept).filter(Concept.concept_id == concept_data["concept_id"]).first()
        if not concept:
            concept = Concept(
                concept_id=concept_data["concept_id"],
                skill_id=concept_data.get("skill_id"),
                name=concept_data["name"],
                description=concept_data.get("description")
            )
            db.add(concept)
            created_concepts += 1

        for pf_data in concept_data.get("pitfalls", []):
            # Upsert Pitfall
            pitfall = db.query(Pitfall).filter(Pitfall.pitfall_id == pf_data["pitfall_id"]).first()
            if not pitfall:
                pitfall = Pitfall(
                    pitfall_id=pf_data["pitfall_id"],
                    concept_id=concept_data["concept_id"],
                    title=pf_data["title"],
                    description=pf_data.get("description"),
                    misconception=pf_data.get("misconception"),
                    correct_mental_model=pf_data.get("correct_mental_model"),
                    severity=pf_data.get("severity", "medium"),
                    remediation_text=pf_data.get("remediation_text"),
                    source="expert",
                    status="active"
                )
                db.add(pitfall)
                created_pitfalls += 1

            for q_data in pf_data.get("questions", []):
                # Upsert Question
                question = db.query(PitfallQuestion).filter(
                    PitfallQuestion.question_id == q_data["question_id"]
                ).first()
                if not question:
                    question = PitfallQuestion(
                        question_id=q_data["question_id"],
                        pitfall_id=pf_data["pitfall_id"],
                        concept_id=concept_data["concept_id"],
                        question_text=q_data["question_text"],
                        options=q_data["options"],
                        correct_option=q_data["correct_option"],
                        explanation=q_data.get("explanation")
                    )
                    db.add(question)
                    created_questions += 1

                for mapping_data in q_data.get("option_mappings", []):
                    mapping_id = f"{q_data['question_id']}_{mapping_data['option_key']}"
                    existing = db.query(PitfallOptionMapping).filter(
                        PitfallOptionMapping.mapping_id == mapping_id
                    ).first()
                    if not existing:
                        mapping = PitfallOptionMapping(
                            mapping_id=mapping_id,
                            question_id=q_data["question_id"],
                            option_key=mapping_data["option_key"],
                            pitfall_id=pf_data["pitfall_id"],
                            misconception_hint=mapping_data.get("misconception_hint")
                        )
                        db.add(mapping)
                        created_mappings += 1

    db.commit()
    print(f"Seeding complete!")
    print(f"  Concepts: {created_concepts}")
    print(f"  Pitfalls: {created_pitfalls}")
    print(f"  Questions: {created_questions}")
    print(f"  Option Mappings: {created_mappings}")


if __name__ == "__main__":
    print("Creating tables and seeding pitfall data...")
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
