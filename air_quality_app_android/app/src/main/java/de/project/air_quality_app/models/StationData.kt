package de.project.air_quality_app.models

import com.google.gson.annotations.SerializedName

data class StationResponse(
    @SerializedName("stations")
    val stations: List<StationData>,
    @SerializedName("count")
    val count: Int,
    @SerializedName("region")
    val region: String? = null
)

data class StationData(
    @SerializedName("id")
    val id: Int,
    @SerializedName("station_uid")
    val stationUid: Int,
    @SerializedName("station_name")
    val stationName: String,
    @SerializedName("aqi")
    val aqi: Int?,
    @SerializedName("pm25")
    val pm25: Double?,
    @SerializedName("pm10")
    val pm10: Double?,
    @SerializedName("no2")
    val no2: Double?,
    @SerializedName("o3")
    val o3: Double?,
    @SerializedName("co")
    val co: Double?,
    @SerializedName("so2")
    val so2: Double?,
    @SerializedName("temperature")
    val temperature: Double?,
    @SerializedName("humidity")
    val humidity: Double?,
    @SerializedName("pressure")
    val pressure: Double?,
    @SerializedName("wind_speed")
    val windSpeed: Double?,
    @SerializedName("latitude")
    val latitude: Double,
    @SerializedName("longitude")
    val longitude: Double,
    @SerializedName("last_update")
    val lastUpdate: String,
    @SerializedName("source")
    val source: String?,
    @SerializedName("region")
    val region: String?
) {
    // Helper function to get AQI color
    fun getAqiColor(): Int {
        return when (aqi) {
            in 0..50 -> 0xFF00E400.toInt()    // Good - Green
            in 51..100 -> 0xFFFFFF00.toInt()  // Moderate - Yellow
            in 101..150 -> 0xFFFF7E00.toInt() // Unhealthy for Sensitive - Orange
            in 151..200 -> 0xFFFF0000.toInt() // Unhealthy - Red
            in 201..300 -> 0xFF8F3F97.toInt() // Very Unhealthy - Purple
            else -> 0xFF7E0023.toInt()        // Hazardous - Maroon
        }
    }
    
    // Helper function to get AQI description
    fun getAqiDescription(): String {
        return when (aqi) {
            in 0..50 -> "Good"
            in 51..100 -> "Moderate"
            in 101..150 -> "Unhealthy for Sensitive Groups"
            in 151..200 -> "Unhealthy"
            in 201..300 -> "Very Unhealthy"
            else -> "Hazardous"
        }
    }
    
    // Helper function to get display name (remove ", Berlin" suffix)
    fun getDisplayName(): String {
        return stationName.replace(", Berlin", "").replace("Berlin-", "")
    }
}
