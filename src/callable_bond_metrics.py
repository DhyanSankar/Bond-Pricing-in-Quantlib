from QuantLib import (
    Date, Settings, UnitedStates, ActualActual,
    Schedule, Period, Semiannual, Following,
    DateGeneration, YieldTermStructureHandle, FlatForward,
    CallableFixedRateBond, CallabilitySchedule, Callability, CallabilityPrice,
    TreeCallableFixedRateBondEngine, BinomialCoxRossRubinstein,
    Compounded, Frequency, CashFlows, BondFunctions
)

# ---------- Callable Bond Setup ----------
today = Date(21, 4, 2025)
Settings.instance().evaluationDate = today
calendar = UnitedStates(UnitedStates.GovernmentBond)
business_convention = Following
day_count = ActualActual(ActualActual.Bond)
settlement_days = 2
face_amount = 1000
coupon_rate = 0.05
frequency = Semiannual
issue_date = Date(21, 4, 2020)
maturity_date = Date(21, 4, 2030)
flat_rate = 0.04

schedule = Schedule(issue_date, maturity_date, Period(frequency), calendar,
                    business_convention, business_convention,
                    DateGeneration.Backward, False)

rate_handle = YieldTermStructureHandle(FlatForward(today, flat_rate, day_count))

# Setup call schedule
call_schedule = CallabilitySchedule()
call_price = CallabilityPrice(100.0, CallabilityPrice.Clean)
for year in range(2026, 2030):
    call_date = Date(21, 4, year)
    call_schedule.append(Callability(call_price, Callability.Call, call_date))

# Callable bond setup
callable_bond = CallableFixedRateBond(settlement_days, face_amount, schedule, [coupon_rate], day_count,
                                      business_convention, face_amount, issue_date, call_schedule)
callable_bond.setPricingEngine(TreeCallableFixedRateBondEngine(
    BinomialCoxRossRubinstein(rate_handle, 200)))

ytws = []
durations_to_worst = []
convexities_to_worst = []

for callability in call_schedule:
    call_date = callability.date()
    try:
        ytc = CashFlows.yieldRate(callable_bond.cashflows(), callable_bond.cleanPrice(), day_count,
                                  Compounded, frequency, False, call_date)
        ytws.append(ytc)
        durations_to_worst.append(
            BondFunctions.duration(callable_bond, ytc, day_count, Compounded, frequency, Duration.Modified))
        convexities_to_worst.append(
            BondFunctions.convexity(callable_bond, ytc, day_count, Compounded, frequency))
    except RuntimeError:
        continue

ytw = min(ytws) if ytws else None
mod_duration_to_worst = durations_to_worst[ytws.index(ytw)] if ytw else None
convexity_to_worst = convexities_to_worst[ytws.index(ytw)] if ytw else None

print("=== Callable Bond ===")
print("Yield to Worst:", round(ytw, 6) if ytw else "N/A")
print("Mod Duration to Worst:", round(mod_duration_to_worst, 6) if mod_duration_to_worst else "N/A")
print("Convexity to Worst:", round(convexity_to_worst, 6) if convexity_to_worst else "N/A")
