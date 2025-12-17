# Validation script for Example 7: Censoring Effect (Aggregated)

# Load the LWP-TRENDS functions
suppressWarnings({
    source("../../Example_Files/R/LWPTrends_v2502/LWPTrends_v2502.r")
})

# Define the scenarios to test
scenarios <- c("0pct", "20pct", "40pct", "60pct")
output_dir <- "."

cat("--- LWP-TRENDS Aggregated Analysis Results for Example 7 ---\n")

# Loop through each scenario, read data, and run the analysis
for (name in scenarios) {
    # --- Read and Prepare Data ---
    file_path <- file.path(output_dir, sprintf("validation_data_%s.csv", name))
    data <- read.csv(file_path)

    # --- Pre-process the data ---
    data <- RemoveAlphaDetect(data, ColToUse = "Value")
    data$myDate <- as.Date(data$Date)
    data$Year <- format(data$myDate, "%Y")
    data$TimeIncr <- data$Year # Data is annual
    data <- GetMoreDateInfo(data)

    # --- Run the non-seasonal trend analysis in AGGREGATED mode ---
    result <- NonSeasonalTrendAnalysis(
        data,
        ValuesToUse = "RawValue",
        Year = "Year",
        TimeIncrMed = TRUE # Use the aggregated workflow
    )

    # --- Print the key results ---
    cat(sprintf("\n--- Scenario: %s Censoring ---\n", name))
    cat(sprintf("%-12s | %-10s | %-10s | %-10s | %s\n", "Method", "P-value", "Z-stat", "Slope", "90% CI"))
    cat(paste(rep("-", 65), collapse = ""), "\n")

    ci_str <- sprintf("[%.3f, %.3f]", result$Sen_Lci, result$Sen_Uci)
    cat(sprintf("%-12s | %-10.4f | %-10.4f | %-10.4f | %s\n",
                "LWP-TRENDS", result$p, result$Z, result$AnnualSenSlope, ci_str))
}

cat("\n=================================================================\n")
