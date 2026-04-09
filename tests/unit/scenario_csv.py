"""Shared CSV test data for scenario definition tests."""

CSV_HEADER = (
    "Number,Product,"
    "Efficacy mean,Efficacy STD,"
    "Adherence mean,Adherence STD,"
    "Target Coverage mean,Target Coverage STD,"
    "Target Year mean,Target Year STD,"
    "Target Population,Sex\n"
)

# Single-row intervention (one target population/sex per scenario)
MINIMAL_CSV = CSV_HEADER + "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,High risk heterosexual,Female\n"

# Multi-row scenario 1 (two target rows), single-row scenario 2, combined scenario 3
COMBINED_CSV = CSV_HEADER + (
    "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,High risk heterosexual,Female\n"
    "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,Men who have sex with men,Male\n"
    "2,One month pill for PrEP,0.95,0.03,0.95,0.03,0.20,0.05,2028,2,High risk heterosexual,Female\n"
    "3,1+2,,,,,,,,,,\n"
)
