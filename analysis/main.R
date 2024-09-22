library(here)


plot_arctic_search <- function() {
  library(jsonlite)
  
  filename <- "keyword_search_results.json"
  json_data <- fromJSON(filename)
  df <- as.data.frame(json_data)
  
  title <- (
    "Frequency of Keyword 'arctic' in Congressional Legislation Filtered by Armed Forces and National Security (1987-2024)"
  )
  
  png(
    filename = "plot_arctic_search.png",
    width = 1920,
    height = 1080,
    units = "px",
    res = 100
  )
  
  # Increase the bottom margin to accommodate rotated labels
  par(
    mar = c(8, 6, 4, 2), # Adjust margins
    cex.main = 1.75 # Increase the font size of the main title
  )
  
  keyword_plot <- barplot(df$arctic_count,
                          names.arg = df$congress,
                          main = title,
                          xlab = "",
                          ylab = "",
                          col = "skyblue", border = FALSE,
                          xaxt = "n", # Suppress the default x-axis
                          yaxt = "n", # Suppress the default y-axis
                          width = 0.5
  )
  
  # Add custom x-axis ticks without labels
  axis(1, at = keyword_plot, labels = FALSE)
  
  # Add rotated x-axis tick labels
  text(
    x = keyword_plot,
    y = par("usr")[3] - max(df$arctic_count) * 0.025,
    labels = df$congress,
    srt = 60,
    adj = 1,
    xpd = TRUE,
    cex = 0.75
  )
  
  # Add y-axis with rotated labels
  axis(2, las = 2) # las = 2 rotates y-axis labels to be perpendicular to axis
  
  # Add x-axis title using mtext
  mtext("Congressional Session", side = 1, line = 6, cex = 1.75)
  
  # Close the PNG device
  dev.off()
}



main <- function() {
  plot_arctic_search()
}

main()