"""Generate deterministic synthetic onboarding-experiment observations."""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"


def generate_experiment(n: int = 24_000, seed: int = 78149) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    user_id = np.arange(1, n + 1)
    treatment = rng.binomial(1, 0.5, n)
    device = rng.choice(["ios", "android", "web"], n, p=[0.36, 0.34, 0.30])
    channel = rng.choice(["organic", "paid", "referral"], n, p=[0.48, 0.34, 0.18])
    prior_activity = np.clip(rng.gamma(2.0, 1.6, n), 0, 12)

    base_logit = -0.60 + 0.10 * prior_activity + 0.13 * (device == "ios") - 0.08 * (channel == "paid")
    treatment_effect = 0.16 + 0.08 * (device == "android") - 0.04 * (channel == "paid")
    activation_probability = 1 / (1 + np.exp(-(base_logit + treatment * treatment_effect)))
    activated_7d = rng.binomial(1, activation_probability)

    support_probability = np.clip(0.083 - 0.004 * treatment + 0.012 * (device == "android"), 0.01, 0.25)
    support_contact_7d = rng.binomial(1, support_probability)
    latency = rng.normal(420 + 5 * treatment + 18 * (device == "android"), 92, n).clip(80)

    pre_engagement = rng.normal(3.5 + 0.25 * prior_activity, 1.1, n).clip(0)
    post_engagement = pre_engagement + 0.25 + 0.32 * treatment + rng.normal(0, 0.85, n)

    return pd.DataFrame(
        {
            "user_id": user_id,
            "treatment": treatment,
            "device": device,
            "channel": channel,
            "prior_activity": prior_activity,
            "activated_7d": activated_7d,
            "support_contact_7d": support_contact_7d,
            "transaction_latency_ms": latency,
            "pre_engagement": pre_engagement,
            "post_engagement": post_engagement,
        }
    )


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    frame = generate_experiment()
    frame.to_csv(DATA_DIR / "experiment_users.csv", index=False)
    print(f"Wrote {len(frame):,} synthetic users to {DATA_DIR / 'experiment_users.csv'}")


if __name__ == "__main__":
    main()

