package de.project.air_quality_app.utils

import de.project.air_quality_app.models.StationData
import kotlin.math.*

object LocationUtils {
    
    /**
     * Berechnet die Entfernung zwischen zwei Koordinaten in Metern
     * Verwendet die Haversine-Formel
     */
    fun calculateDistance(
        lat1: Double, lon1: Double,
        lat2: Double, lon2: Double
    ): Double {
        val earthRadiusKm = 6371.0
        
        val dLat = Math.toRadians(lat2 - lat1)
        val dLon = Math.toRadians(lon2 - lon1)
        
        val a = sin(dLat / 2) * sin(dLat / 2) +
                cos(Math.toRadians(lat1)) * cos(Math.toRadians(lat2)) *
                sin(dLon / 2) * sin(dLon / 2)
        
        val c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return earthRadiusKm * c * 1000 // Convert to meters
    }
    
    /**
     * Findet die nächstgelegene Station zu einem gegebenen Standort
     */
    fun findNearestStation(
        userLat: Double,
        userLon: Double,
        stations: List<StationData>
    ): Pair<StationData, Double>? {
        if (stations.isEmpty()) return null
        
        return stations.map { station ->
            val distance = calculateDistance(
                userLat, userLon,
                station.latitude, station.longitude
            )
            station to distance
        }.minByOrNull { it.second }
    }
    
    /**
     * Sortiert Stationen nach Entfernung zum Benutzer
     */
    fun sortStationsByDistance(
        userLat: Double,
        userLon: Double,
        stations: List<StationData>
    ): List<Pair<StationData, Double>> {
        return stations.map { station ->
            val distance = calculateDistance(
                userLat, userLon,
                station.latitude, station.longitude
            )
            station to distance
        }.sortedBy { it.second }
    }
    
    /**
     * Formatiert Entfernung für die Anzeige
     */
    fun formatDistance(distanceInMeters: Double): String {
        return when {
            distanceInMeters < 1000 -> "${distanceInMeters.toInt()}m"
            else -> "${"%.1f".format(distanceInMeters / 1000)}km"
        }
    }
    
    /**
     * Überprüft ob sich der Benutzer in Berlin befindet (grober Check)
     */
    fun isInBerlinArea(lat: Double, lon: Double): Boolean {
        val berlinBounds = mapOf(
            "lat_min" to 52.35,
            "lat_max" to 52.65,
            "lon_min" to 13.10,
            "lon_max" to 13.70
        )
        
        return lat >= berlinBounds["lat_min"]!! && lat <= berlinBounds["lat_max"]!! &&
               lon >= berlinBounds["lon_min"]!! && lon <= berlinBounds["lon_max"]!!
    }
}
