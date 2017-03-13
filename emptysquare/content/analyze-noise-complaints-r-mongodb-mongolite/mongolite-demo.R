# install mongolite, leaflet, lubridate, mapview, sp (or is it included?)
library(ggplot2)
library(graphics)
library(lubridate)
library(mongolite)
library(mapview)
library(sp)
library(dplyr)


options(error=function() dump.frames(to.file=TRUE)) 

mdb <- mongo("three_eleven", url = "mongodb://localhost/test")
# Results are in UTC - get all before midnight March 1, New York time.
results <- mdb$find('{
  "location": {
    "$geoWithin": {
     "$centerSphere": [[-73.98891066960417,40.72078970710123], 0.00006823637430874053]
    }
  },
  "created": {"$lt": {"$date": "2017-03-01T00:00:00.000Z"}}
}')

# Extract lon/lot from GeoJSON like {type: "Point", coordinates: [1, 2]}
coords <- results$location['coordinates'][[1]]
lons <- sapply(coords, function (x) x[1])
lats <- sapply(coords, function (x) x[2])

# Convert from UTC to US Eastern, very crudely.
created <- as.POSIXct(results$created, origin = "1970-01-01 05:00:00")
complaints <- data.frame(
  lons = lons,
  lats = lats,
  type = results$complaintType,
  created = created,
  month = floor_date(created, "month"),
  is_noise = grepl("noise", results$complaintType, ignore.case = TRUE)
)

by_month = summarise(
  group_by(complaints, month),
  count = n(),
  pct_noise = 100 * sum(is_noise) / n())

plot(select(by_month, month, count), pch = 16, cex = 1.5, col = "#707070", main = "Complaints")
abline(lm(by_month$count ~ by_month$month))

plot(select(by_month, month, pct_noise), pch = 16, cex = 1.5, col = "#707070", main = "% Noise Complaints")
abline(lm(by_month$pct_noise ~ by_month$month))

coordinates(complaints) <- ~lons + lats
months <- seq(as.POSIXct("2010-01-01"), to = as.POSIXct("2017-03-01"), by = "month")
for (m in months)
{
  month_complaints <- subset(complaints, month == m)
  map <- mapview(SpatialPoints(month_complaints, proj4string = CRS("+proj=longlat")))
  mapshot(map, file = paste0(m, ".png"))
}
