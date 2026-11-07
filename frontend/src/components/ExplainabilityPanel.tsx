import {
  Brain,
  TrendingUp,
  TrendingDown,
  Info,
  ChevronDown,
  Activity,
} from "lucide-react";

interface ExplanationFactor {
  feature: string;
  label: string;
  value: number;
  baseline_value: number;
  contribution: number;
  direction:
    | "increases_concern"
    | "decreases_concern"
    | "neutral";
}

interface Explanation {
  method: string;
  baseline_source: string;
  increasing_factors: ExplanationFactor[];
  decreasing_factors: ExplanationFactor[];
  neutral_factors: ExplanationFactor[];
  all_factors: ExplanationFactor[];
  note: string;
}

interface ExplainabilityPanelProps {
  explanation: Explanation;
}

function formatValue(feature: string, value: number) {
  if (feature === "sleep_hours" ||
      feature === "screen_time" ||
      feature === "study_hours") {
    return `${value.toFixed(1)} hours`;
  }

  if (feature === "exercise_minutes") {
    return `${value.toFixed(0)} min`;
  }

  return value.toFixed(1);
}

function FactorCard({
  factor,
  direction,
  maxContribution,
}: {
  factor: ExplanationFactor;
  direction: "increases_concern" | "decreases_concern";
  maxContribution: number;
}) {
  const isIncreasing = direction === "increases_concern";

  const barWidth =
    maxContribution > 0
      ? (Math.abs(factor.contribution) / maxContribution) * 100
      : 0;

  return (
    <div
      className={`xai-factor ${
        isIncreasing ? "xai-increasing" : "xai-decreasing"
      }`}
    >
      <div className="xai-factor-top">
        <div className="xai-factor-name">
          {isIncreasing ? (
            <TrendingUp size={17} />
          ) : (
            <TrendingDown size={17} />
          )}

          <strong>{factor.label}</strong>
        </div>

        <span className="xai-contribution">
          {factor.contribution > 0 ? "+" : ""}
          {factor.contribution.toFixed(3)}
        </span>
      </div>

      <div className="xai-progress-track">
        <div
          className="xai-progress-fill"
          style={{ width: `${barWidth}%` }}
        />
      </div>

      <div className="xai-factor-values">
        <span>
          Your value:{" "}
          <strong>
            {formatValue(factor.feature, factor.value)}
          </strong>
        </span>

        <span>
          Training average:{" "}
          <strong>
            {formatValue(
              factor.feature,
              factor.baseline_value
            )}
          </strong>
        </span>
      </div>
    </div>
  );
}

function ExplainabilityPanel({
  explanation,
}: ExplainabilityPanelProps) {
  const maxContribution = Math.max(
    0,
    ...explanation.all_factors.map((factor) =>
      Math.abs(factor.contribution)
    )
  );

  return (
    <section className="xai-panel">
      <div className="xai-header">
        <div className="xai-header-icon">
          <Brain size={21} />
        </div>

        <div>
          <span className="xai-eyebrow">
            MODEL EXPLAINABILITY
          </span>

          <h3>Why this score?</h3>

          <p>
            Understand which of your responses influenced
            the structured model's estimate.
          </p>
        </div>
      </div>

      <div className="xai-summary">
        <div className="xai-summary-icon">
          <Activity size={18} />
        </div>

        <p>
          The model compares your responses with average
          values from its training dataset and calculates
          how each feature influences its prediction.
        </p>
      </div>

      {explanation.increasing_factors.length > 0 && (
        <div className="xai-group">
          <div className="xai-group-heading increasing">
            <TrendingUp size={18} />

            <div>
              <h4>Factors increasing concern</h4>
              <span>
                These inputs move the model towards a
                higher estimated concern.
              </span>
            </div>
          </div>

          {explanation.increasing_factors.map((factor) => (
            <FactorCard
              key={factor.feature}
              factor={factor}
              direction="increases_concern"
              maxContribution={maxContribution}
            />
          ))}
        </div>
      )}

      {explanation.decreasing_factors.length > 0 && (
        <div className="xai-group">
          <div className="xai-group-heading decreasing">
            <TrendingDown size={18} />

            <div>
              <h4>Factors decreasing concern</h4>
              <span>
                These inputs move the model away from a
                higher estimated concern.
              </span>
            </div>
          </div>

          {explanation.decreasing_factors.map((factor) => (
            <FactorCard
              key={factor.feature}
              factor={factor}
              direction="decreases_concern"
              maxContribution={maxContribution}
            />
          ))}
        </div>
      )}

      {explanation.neutral_factors.length > 0 && (
        <details className="xai-neutral">
          <summary>
            Other factors considered (
            {explanation.neutral_factors.length})
          </summary>

          {explanation.neutral_factors.map((factor) => (
            <FactorCard
              key={factor.feature}
              factor={factor}
              direction="decreases_concern"
              maxContribution={maxContribution}
            />
          ))}
        </details>
      )}

      <details className="xai-method">
        <summary>
          <Info size={16} />
          How is this explanation calculated?
          <ChevronDown size={16} />
        </summary>

        <p>
          Clarity uses Logistic Regression coefficient
          attribution. Each contribution is calculated
          relative to the training dataset mean.
        </p>

        <code>
          Contribution = Coefficient × (Your value − Training average)
        </code>

        <p>
          Positive contributions move the model towards
          higher concern. Negative contributions move it
          towards lower concern.
        </p>

        <p>
          These values are log-odds contributions, not
          percentages. They explain only the structured
          model, not the entire final multimodal score.
        </p>
      </details>

      <div className="xai-disclaimer">
        <Info size={17} />

        <p>{explanation.note}</p>
      </div>
    </section>
  );
}

export default ExplainabilityPanel;