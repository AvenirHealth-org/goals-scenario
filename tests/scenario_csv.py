CSV_HEADER = (
    "Number,Product,"
    "Efficacy mean,Efficacy STD,"
    "Adherence mean,Adherence STD,"
    "Target Coverage mean,Target Coverage STD,"
    "Target Year mean,Target Year STD,"
    "Target Population,Sex\n"
)

MINIMAL_CSV = CSV_HEADER + "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,key_pops,both\n"

COMBINED_CSV = CSV_HEADER + (
    "1,Daily PrEP,0.95,0.03,0.80,0.20,0.10,0.05,2027,2,key_pops,both\n"
    "2,One month pill for PrEP,0.95,0.03,0.95,0.03,0.20,0.05,2028,2,key_pops,both\n"
    "3,1+2,,,,,,,,,,\n"
)
