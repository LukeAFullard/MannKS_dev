# Validation script for Right-Censored and Mixed-Censored Data Analysis

# Load the LWP-TRENDS functions
suppressWarnings({
    source("Example_Files/R/LWPTrends_v2502/LWPTrends_v2502.r")
})

# Define the scenarios to test
scenarios <- c("right_censored", "mixed_censored")
output_dir <- "validation/08_Right_Censored_Data"

cat("--- LWP-TRENDS Analysis Results ---\n")

# Loop through each scenario, read data, and run the analysis
for (name in scenarios) {
    # --- Read and Prepare Data ---
    file_path <- file.path(output_dir, sprintf("validation_data_%s.csv", name))
    data <- read.csv(file_path)

    # LWP script expects specific column names
    names(data)[names(data) == "time"] <- "TimeIncr"
    names(data)[names(data) == "value_for_manken"] <- "Value"

    # Remove pre-existing logical columns to avoid the LWP bug
    data$Censored <- NULL
    data$CenType <- NULL

    # --- Run the non-seasonal trend analysis ---
    # We disable aggregation to match the Python script's behavior.
    # Note: This will likely fail for the "mixed_censored" case due to the previously identified bug.
    result <- try(NonSeasonalTrendAnalysis(
        data,
        ValuesToUse = "Value",
        Year = "TimeIncr",
        TimeIncrMed = FALSE, # Disable time aggregation
        UseMidObs = FALSE    # Disable aggregation to middle observation
    ), silent = TRUE)

    # --- Print the key results ---
    cat(sprintf("\n--- Scenario: %s ---\n", gsub("_", " ", name)))
    cat(sprintf("%-12s | %-10s | %-10s | %-10s | %s\n", "Method", "P-value", "Z-stat", "Slope", "90% CI"))
    cat(paste(rep("-", 65), collapse = ""), "\n")

    if (inherits(result, "try-error")) {
        cat("LWP-TRENDS script failed to run. See README for bug analysis.\n")
    } else {
        ci_str <- sprintf("[%.3f, %.3f]", result$Sen_Lci, result$Sen_Uci)
        cat(sprintf("%-12s | %-10.4f | %-10.4f | %-10.4f | %s\n",
                    "LWP-TRENDS", result$p, result$Z, result$AnnualSenSlope, ci_str))
    }
}

cat("\n=================================================================\n")
