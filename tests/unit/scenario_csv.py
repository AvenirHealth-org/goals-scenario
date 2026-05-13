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

# Scenario 1 has two different products (multi-intervention single scenario)
MULTI_PRODUCT_CSV = CSV_HEADER + (
    "1,One month pill for PrEP,0.95,0.03,0.95,0.03,0.20,0.05,2028,2,High risk heterosexual,Female\n"
    "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,High risk heterosexual,Female\n"
    "2,One month injectable PrEP,0.98,0.01,0.98,0.01,0.10,0.05,2027,2,High risk heterosexual,Female\n"
)

# Three different products across three populations in scenario 1, plus combined scenario 3 = 1+2
MULTI_PRODUCT_MULTI_POP_CSV = CSV_HEADER + (
    "1,One month pill for PrEP,0.95,0.03,0.95,0.03,0.20,0.05,2028,2,High risk heterosexual,Female\n"
    "1,Six month injectable PrEP,0.99,0.01,0.99,0.01,0.20,0.05,2028,2,Men who have sex with men,Male\n"
    "1,bNABs,0.90,0.05,0.99,0.02,0.20,0.02,2030,2,Medium risk heterosexual,Female\n"
    "2,One month injectable PrEP,0.95,0.05,0.85,0.05,0.30,0.05,2030,2,Medium risk heterosexual,Female\n"
    "3,1+2,,,,,,,,,,\n"
)
