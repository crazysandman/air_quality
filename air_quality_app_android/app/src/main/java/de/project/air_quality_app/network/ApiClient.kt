package de.project.air_quality_app.network

import de.project.air_quality_app.Constants
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(Constants.BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    val airQualityApiService: AirQualityApiService by lazy {
        retrofit.create(AirQualityApiService::class.java)
    }
}
