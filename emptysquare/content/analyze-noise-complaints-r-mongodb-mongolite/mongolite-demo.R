# Prerequisites: install mongolite, lubridate, dplyr, and ggmap.
#
# I've had issues with current ggmap, try an older version as a workaround:
#
#   install.packages("devtools")
#   devtools::install_github("dkahle/ggmap")
#   devtools::install_github("hadley/ggplot2@v2.2.0")

library(ggmap)
library(lubridate)
library(mongolite)
library(dplyr)

mdb <- mongo("three_eleven", url = "mongodb://localhost/test")

get_complaints <- function(query) {
    res <- mdb$find(query)
    # Extract lon/lat from GeoJSON
    # like {type: "Point", coordinates: [1, 2]}
    coords <- res$location['coordinates'][[1]]
    lons <- sapply(coords, function (x) x[1])
    lats <- sapply(coords, function (x) x[2])

    # Convert from UTC to US Eastern, very crudely.
    created <-
    as.POSIXct(res$created, origin = "1970-01-01 05:00:00")
    data.frame(
        lons = lons,
        lats = lats,
        type = res$complaintType,
        created = created,
        month = floor_date(created, "month"),
        is_noise = grepl(
            "noise",
            res$complaintType,
            ignore.case = TRUE
        )
    )
}

# 2nd centerSphere param is radians.
# To convert from meters, div by 6378100.
# Get all complaints within 500 meters of
# my apartment before midnight March 1 UTC.
complaints <- get_complaints('{
    "location": {
        "$geoWithin": {
            "$centerSphere": [
                [-73.98891066960417,40.72078970710123],
                0.00007839325190887568
            ]
        }
    },
    "created": {
        "$lt": {"$date": "2017-03-01T00:00:00.000Z"}
    }
}')

by_month = summarise(
    group_by(complaints, month),
    count = n(),
    pct_noise = 100 * sum(is_noise) / n()
)

plot(
    select(by_month, month, count),
    pch = 16,
    cex = 1.5,
    col = "#707070",
    main = "Complaints"
)

abline(lm(by_month$count ~ by_month$month))

plot(
    select(by_month, month, pct_noise),
    pch = 16,
    cex = 1.5,
    col = "#707070",
    main = "% Noise Complaints"
)

abline(lm(by_month$pct_noise ~ by_month$month))

# Get only noise complaints, for a 1km around.
noise_complaints <- get_complaints('{
    "complaintType": {"$regex": "noise", "$options": "i"},
    "location": {
        "$geoWithin": {
            "$centerSphere": [
                [-73.98891066960417,40.72078970710123],
                0.00015678650381775137
            ]
        }
    },
    "created": {
        "$lt": {"$date": "2017-03-01T00:00:00.000Z"}
    }
}')

orchard_st = data.frame(
    lon = -73.98891066960417,
    lat = 40.72078970710123
)

orchard_st_map <- ggmap(
    get_map(
    location = orchard_st,
    color = "bw", zoom = 16
), extent = "device")

orchard_st_marker = geom_point(
    aes(x=lon, y=lat), color="#00cc00",
    size=4, data = orchard_st
)

orchard_st_map +
geom_point(
    aes(x = lons, y = lats),
    colour = "red",
    alpha = 0.1,
    size = 2,
    data = noise_complaints
) + orchard_st_marker

orchard_st_map +
geom_density2d(
    data = noise_complaints,
    aes(x = lons, y = lats),
    size = 0.3
) + stat_density2d(
    data = noise_complaints,
    aes(x = lons, y = lats, fill = ..level.., alpha = ..level..),
    size = 0.01,
    bins = 16,
    geom = "polygon"
) + scale_fill_gradient(low = "green", high = "red") +
scale_alpha(range = c(0, 0.3), guide = FALSE)
