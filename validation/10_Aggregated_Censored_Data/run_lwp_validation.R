# Validation script for Aggregated Censored Data Analysis

# Load the LWP-TRENDS functions
suppressWarnings({
    source("Example_Files/R/LWPTrends_v2502/LWPTrends_v2502.r")
})

output_dir <- "validation/10_Aggregated_Censored_Data"

cat("--- LWP-TRENDS Aggregated Censored Data Validation ---\n")

# --- Read and Prepare Data ---
file_path <- file.path(output_dir, "validation_data_aggregated.csv")
data <- read.csv(file_path)

# LWP script expects specific column names and needs date info
names(data)[names(data) == "Value"] <- "Value"
names(data)[names(data) == "Year"] <- "Year"
data$myDate <- as.Date(paste(data$Year, "-06-01", sep="")) # Use mid-year for date
data <- GetMoreDateInfo(data)
data$TimeIncr <- data$Year # Aggregate by Year

# --- Run analysis with default aggregation ---
result <- NonSeasonalTrendAnalysis(
    data,
    ValuesToUse = "Value",
    Year = "Year"
    # TimeIncrMed = TRUE by default
)

cat(sprintf("%-25s | %-10s | %-10s | %-10s | %s\n", "Method", "P-value", "Z-stat", "Slope", "90% CI"))
cat(paste(rep("-", 75), collapse = ""), "\n")
ci_str <- sprintf("[%.3f, %.3f]", result$Sen_Lci, result$Sen_Uci)
cat(sprintf("%-25s | %-10.4f | %-10.4f | %-10.4f | %s\n",
            "LWP-TRENDS (Aggregated)", result$p, result$Z, result$AnnualSenSlope, ci_str))

cat("\n===========================================================================\n")
