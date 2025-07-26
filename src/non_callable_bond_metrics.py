from QuantLib import (
    Date, Settings, UnitedStates, ActualActual,
    Schedule, Period, Semiannual, Following,
    DateGeneration, YieldTermStructureHandle,
    FlatForward, FixedRateBond, DiscountingBondEngine,
    Compounded, Duration, BondFunctions
)

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

bond = FixedRateBond(settlement_days, face_amount, schedule, [coupon_rate], day_count)
bond.setPricingEngine(DiscountingBondEngine(rate_handle))

ytm = bond.bondYield(day_count, Compounded, frequency)
mod_duration = BondFunctions.duration(bond, ytm, day_count, Compounded, frequency, Duration.Modified)
duration = BondFunctions.duration(bond, ytm, day_count, Compounded, frequency, Duration.Macaulay)
convexity = BondFunctions.convexity(bond, ytm, day_count, Compounded, frequency)

def compute_effective_metrics(bond, yield_curve, shift_bp=1.0):
    shift = shift_bp / 10000
    base_price = bond.cleanPrice()

    up_curve = YieldTermStructureHandle(FlatForward(today, flat_rate + shift, day_count))
    bond.setPricingEngine(DiscountingBondEngine(up_curve))
    up_price = bond.cleanPrice()

    down_curve = YieldTermStructureHandle(FlatForward(today, flat_rate - shift, day_count))
    bond.setPricingEngine(DiscountingBondEngine(down_curve))
    down_price = bond.cleanPrice()

    bond.setPricingEngine(DiscountingBondEngine(yield_curve))

    eff_duration = (down_price - up_price) / (2 * base_price * shift)
    eff_convexity = (up_price + down_price - 2 * base_price) / (base_price * shift**2)
    return eff_duration, eff_convexity

eff_duration, eff_convexity = compute_effective_metrics(bond, rate_handle)

print("Bond Metrics:")
print("Yield to Maturity:", round(ytm, 6))
print("Modified Duration:", round(mod_duration, 6))
print("Macaulay Duration:", round(duration, 6))
print("Convexity:", round(convexity, 6))
print("Effective Duration:", round(eff_duration, 6))
print("Effective Convexity:", round(eff_convexity, 6))
