
options(repos = c(CRAN = "https://cloud.r-project.org"))

install_if_missing <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    message(paste("Installing", pkg))
    install.packages(pkg)
  }
}

# Core dependencies
install_if_missing("plyr")
install_if_missing("tidyr")
install_if_missing("viridis")
install_if_missing("lubridate")
install_if_missing("gam")

# NADA and its dependencies (sometimes tricky)
install_if_missing("NADA")

# Visualization
install_if_missing("ggplot2")
