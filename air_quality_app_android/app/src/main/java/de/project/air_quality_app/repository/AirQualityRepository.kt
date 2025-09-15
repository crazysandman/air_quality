package de.project.air_quality_app.repository

import de.project.air_quality_app.models.StationData
import de.project.air_quality_app.network.ApiClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class AirQualityRepository {
    private val apiService = ApiClient.airQualityApiService
    
    suspend fun getBerlinStations(): Result<List<StationData>> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getBerlinStations()
                if (response.isSuccessful && response.body() != null) {
                    Result.success(response.body()!!.stations)
                } else {
                    Result.failure(Exception("API Error: ${response.code()} - ${response.message()}"))
                }
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
    
    suspend fun checkHealth(): Result<Boolean> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getHealthStatus()
                Result.success(response.isSuccessful)
            } catch (e: Exception) {
                Result.failure(e)
            }
        }
    }
}
