package de.project.air_quality_app.network

import de.project.air_quality_app.models.StationResponse
import retrofit2.Response
import retrofit2.http.GET

interface AirQualityApiService {
    @GET("stations/berlin")
    suspend fun getBerlinStations(): Response<StationResponse>
    
    @GET("stations/latest")
    suspend fun getLatestStations(): Response<StationResponse>
    
    @GET("health")
    suspend fun getHealthStatus(): Response<Map<String, Any>>
}
