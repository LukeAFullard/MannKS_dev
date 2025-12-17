# Validation script for Aggregated Censored Data Analysis

# Load the LWP-TRENDS functions
suppressWarnings({
    source("../../Example_Files/R/LWPTrends_v2502/LWPTrends_v2502.r")
})

output_dir <- "."

cat("--- LWP-TRENDS Aggregated Censored Data Validation ---\n")

# --- Read and Prepare Data ---
file_path <- file.path(output_dir, "validation_data_aggregated.csv")
data <- read.csv(file_path)

# --- Pre-process the data ---
# This calls the helper function to create the RawValue, Censored, and CenType columns.
data <- RemoveAlphaDetect(data, ColToUse = "Value")

# LWP script needs date info
data$myDate <- as.Date(paste(data$Year, "-06-01", sep="")) # Use mid-year for date
data <- GetMoreDateInfo(data)
data$TimeIncr <- data$Year # Aggregate by Year

# --- Run analysis with default aggregation ---
result <- NonSeasonalTrendAnalysis(
    data,
    ValuesToUse = "RawValue",
    Year = "Year",
    TimeIncrMed = TRUE # Explicitly use aggregation
)

cat(sprintf("%-25s | %-10s | %-10s | %-10s | %s\n", "Method", "P-value", "Z-stat", "Slope", "90% CI"))
cat(paste(rep("-", 75), collapse = ""), "\n")

ci_str <- sprintf("[%.3f, %.3f]", result$Sen_Lci, result$Sen_Uci)
cat(sprintf("%-25s | %-10.4f | %-10.4f | %-10.4f | %s\n",
            "LWP-TRENDS (Aggregated)", result$p, result$Z, result$AnnualSenSlope, ci_str))

cat("\n===========================================================================\n")
