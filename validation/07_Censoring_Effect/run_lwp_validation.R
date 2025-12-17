# Validation script for Censoring Effect Analysis
# NOTE: This script is expected to FAIL.
# It is preserved here to document a bug in the underlying `LWPTrends_v2502.r` script.
# The bug occurs when analyzing non-aggregated (`TimeIncrMed = FALSE`) censored data.
# The `ValueForTimeIncr` function incorrectly converts the `Censored` logical column
# to a character vector, which causes a fatal `invalid argument type` error downstream
# in the `GetAnalysisNote` function. See the README.md in this directory for a full analysis.

# Load the LWP-TRENDS functions
suppressWarnings({
    source("Example_Files/R/LWPTrends_v2502/LWPTrends_v2502.r")
})

# Define the censoring proportions to test
censor_proportions <- c(0, 20, 40, 60)
output_dir <- "validation/07_Censoring_Effect"

cat("--- LWP-TRENDS Analysis Results ---\n")
cat("--- NOTE: This script is expected to fail due to a bug in the LWP-TRENDS source. ---\n")

# Loop through each proportion, read data, and run the analysis
for (prop in censor_proportions) {
    # --- Read and Prepare Data ---
    file_path <- file.path(output_dir, sprintf("validation_data_%dpct.csv", prop))
    data <- read.csv(file_path)

    names(data)[names(data) == "time"] <- "TimeIncr"
    names(data)[names(data) == "original_value"] <- "RawValue"
    names(data)[names(data) == "value_for_manken"] <- "Value"

    # --- Run the non-seasonal trend analysis ---
    # This call will fail for any dataset with censored data (prop > 0)
    # because of the bug described at the top of this file.
    result <- NonSeasonalTrendAnalysis(
        data,
        ValuesToUse = "Value",
        Year = "TimeIncr",
        TimeIncrMed = FALSE, # This setting triggers the bug
        UseMidObs = FALSE
    )

    # --- Print the key results (will not be reached) ---
    cat(sprintf("\n--- Censoring Level: %d%% ---\n", prop))
    cat(sprintf("%-12s | %-10s | %-10s | %-10s | %s\n", "Method", "P-value", "Z-stat", "Slope", "90% CI"))
    cat(paste(rep("-", 65), collapse = ""), "\n")

    ci_str <- sprintf("[%.3f, %.3f]", result$Sen_Lci, result$Sen_Uci)
    cat(sprintf("%-12s | %-10.4f | %-10.4f | %-10.4f | %s\n",
                "LWP-TRENDS", result$p, result$Z, result$AnnualSenSlope, ci_str))
}

cat("\n=================================================================\n")
