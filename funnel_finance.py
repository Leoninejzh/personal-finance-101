"""
Strict funnel cashflow: take-home minus living buckets, then investing, then remainder.

Formulas (order is fixed):
  SavingBeforeInvesting = Income - Housing - Car - Child - Grocery - Entertainment
  SavingAfterInvesting  = SavingBeforeInvesting - Investing_applied

``Investing_applied`` is ``min(max(0, Investing_requested), max(0, SavingBeforeInvesting))``
so the invest line never exceeds the pre-invest surplus. If ``SavingBeforeInvesting < 0``,
warnings are returned from ``sync()`` and applied investing is treated as ``0`` for the
after-invest remainder.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FunnelFinanceState:
    """
    Eight floats (defaults 0): ``income``, five living lines, ``investing`` (requested),
    and ``saving_before_investing`` (recomputed by ``sync()``).

    ``saving_after_investing`` and ``investing_applied`` are derived; see ``as_dict()``
    for a full flat map including those two.
    """

    income: float = 0.0
    housing: float = 0.0
    car: float = 0.0
    child: float = 0.0
    grocery: float = 0.0
    entertainment: float = 0.0
    investing: float = 0.0
    saving_before_investing: float = 0.0

    def investing_applied(self) -> float:
        """Dollars counted against surplus after cap (uses current ``saving_before_investing``)."""
        s_before = float(self.saving_before_investing)
        raw_inv = max(0.0, float(self.investing))
        if s_before <= 0:
            return 0.0
        return min(raw_inv, s_before)

    @property
    def saving_after_investing(self) -> float:
        """Saving before investing, minus applied investing (call ``sync()`` first)."""
        return float(self.saving_before_investing) - self.investing_applied()

    def warnings_for_surplus_and_invest_cap(self, lang: str = "en") -> list[str]:
        """
        Warnings for negative **saving_before_investing** or invest request above surplus.
        Call after ``saving_before_investing`` and ``investing`` are set (from ``sync()`` or an override).
        """
        from i18n import text as i18n_text

        warnings: list[str] = []
        s_before = float(self.saving_before_investing)
        raw_inv = max(0.0, float(self.investing))
        if s_before < 0:
            warnings.append(i18n_text("funnel_negative_surplus", lang))
        elif raw_inv > s_before + 1e-9:
            inv_applied = min(raw_inv, s_before)
            warnings.append(
                i18n_text(
                    "funnel_invest_capped",
                    lang,
                    raw=raw_inv,
                    s_before=s_before,
                    inv_applied=inv_applied,
                )
            )
        return warnings

    def sync(self, lang: str = "en") -> list[str]:
        """
        Recompute ``saving_before_investing`` from income minus living lines.
        Returns human-readable warning strings (empty if none).
        """
        s_before = (
            float(self.income)
            - float(self.housing)
            - float(self.car)
            - float(self.child)
            - float(self.grocery)
            - float(self.entertainment)
        )
        self.saving_before_investing = s_before
        return self.warnings_for_surplus_and_invest_cap(lang)

    def as_dict(self) -> dict[str, float]:
        """All line items including derived saving-after and applied invest."""
        return {
            "income": float(self.income),
            "housing": float(self.housing),
            "car": float(self.car),
            "child": float(self.child),
            "grocery": float(self.grocery),
            "entertainment": float(self.entertainment),
            "investing": float(self.investing),
            "saving_before_investing": float(self.saving_before_investing),
            "investing_applied": float(self.investing_applied()),
            "saving_after_investing": float(self.saving_after_investing),
        }


def evaluate_from_inputs(
    income: float,
    housing: float,
    car: float,
    child: float,
    grocery: float,
    entertainment: float,
    investing: float,
    *,
    lang: str = "en",
) -> tuple[FunnelFinanceState, list[str]]:
    """Convenience: build state, run ``sync``, return (state, warnings)."""
    st = FunnelFinanceState(
        income=float(income),
        housing=float(housing),
        car=float(car),
        child=float(child),
        grocery=float(grocery),
        entertainment=float(entertainment),
        investing=float(investing),
    )
    w = st.sync(lang=lang)
    return st, w


if __name__ == "__main__":
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except OSError:
            pass
    demo, warns = evaluate_from_inputs(
        income=8000.0,
        housing=3500.0,
        car=400.0,
        child=0.0,
        grocery=600.0,
        entertainment=300.0,
        investing=5000.0,
    )
    print("as_dict:", demo.as_dict())
    for w in warns:
        print("warning:", w)
