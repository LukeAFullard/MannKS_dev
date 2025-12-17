# Validation script for the HiCensor Rule

# Load the LWP-TRENDS functions
suppressWarnings({
    source("Example_Files/R/LWPTrends_v2502/LWPTrends_v2502.r")
})

output_dir <- "validation/09_HiCensor_Rule"

cat("--- LWP-TRENDS 'HiCensor' Rule Validation ---\n")

# --- Read and Prepare Data ---
file_path <- file.path(output_dir, "validation_data_hicensor.csv")
data <- read.csv(file_path)

# LWP script expects specific column names and needs date info
names(data)[names(data) == "Value"] <- "Value"
names(data)[names(data) == "Year"] <- "Year"
data$myDate <- as.Date(paste(data$Year, "-01-01", sep=""))
data <- GetMoreDateInfo(data) # This adds Month, etc.
data$TimeIncr <- data$Month # Use Month to force aggregation

# --- Run analysis with HiCensor = FALSE ---
cat("\n--- Analysis with HiCensor=FALSE (Default) ---\n")
# Use TimeIncrMed=TRUE to force aggregation and avoid the bug
result_default <- NonSeasonalTrendAnalysis(
    data,
    ValuesToUse = "Value",
    Year = "Year",
    HiCensor = FALSE,
    TimeIncrMed = TRUE
)

cat(sprintf("%-12s | %-10s | %-10s | %-10s | %s\n", "Method", "P-value", "Z-stat", "Slope", "90% CI"))
cat(paste(rep("-", 65), collapse = ""), "\n")
ci_str_default <- sprintf("[%.3f, %.3f]", result_default$Sen_Lci, result_default$Sen_Uci)
cat(sprintf("%-12s | %-10.4f | %-10.4f | %-10.4f | %s\n",
            "LWP-Default", result_default$p, result_default$Z, result_default$AnnualSenSlope, ci_str_default))


# --- Run analysis with HiCensor = TRUE ---
cat("\n--- Analysis with HiCensor=TRUE ---\n")
result_hicensor <- NonSeasonalTrendAnalysis(
    data,
    ValuesToUse = "Value",
    Year = "Year",
    HiCensor = TRUE,
    TimeIncrMed = TRUE
)

cat(sprintf("%-12s | %-10s | %-10s | %-10s | %s\n", "Method", "P-value", "Z-stat", "Slope", "90% CI"))
cat(paste(rep("-", 65), collapse = ""), "\n")
ci_str_hicensor <- sprintf("[%.3f, %.3f]", result_hicensor$Sen_Lci, result_hicensor$Sen_Uci)
cat(sprintf("%-12s | %-10.4f | %-10.4f | %-10.4f | %s\n",
            "LWP-HiCensor", result_hicensor$p, result_hicensor$Z, result_hicensor$AnnualSenSlope, ci_str_hicensor))

cat("\n=================================================================\n")
