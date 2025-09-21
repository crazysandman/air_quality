/**
 * Air Quality ViewModel
 * ====================
 * 
 * MVVM architecture ViewModel managing air quality data and UI state.
 * Handles API calls, location services, and state management for the main screen.
 * 
 * Key Responsibilities:
 * - Fetch air quality data from remote API
 * - Manage user location and GPS functionality
 * - Calculate nearest stations based on user location
 * - Handle loading states and error management
 * - Provide reactive UI state updates via StateFlow
 * 
 * @author Master's Student Project
 * @version 1.0.0
 */

package de.project.air_quality_app.viewmodel

import android.location.Location
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import de.project.air_quality_app.models.StationData
import de.project.air_quality_app.repository.AirQualityRepository
import de.project.air_quality_app.utils.LocationUtils
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * Data class representing user's GPS location coordinates.
 * 
 * @param latitude Geographic latitude coordinate
 * @param longitude Geographic longitude coordinate
 */
data class UserLocation(
    val latitude: Double,
    val longitude: Double
)

/**
 * Comprehensive UI state data class for the Air Quality screen.
 * 
 * Represents all possible states the UI can be in, enabling reactive
 * updates and proper state management throughout the app lifecycle.
 * 
 * @param stations List of air quality monitoring stations
 * @param isLoading Whether data is currently being fetched
 * @param errorMessage Error message if API call failed
 * @param lastUpdate Timestamp of last successful data update
 * @param userLocation Current GPS coordinates of user
 * @param nearestStation Closest station to user with distance
 * @param sortedStations All stations sorted by distance from user
 * @param locationPermissionGranted Whether location permission is granted
 * @param isLocationLoading Whether GPS location is being determined
 */
data class AirQualityUiState(
    val stations: List<StationData> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val lastUpdate: String? = null,
    val userLocation: UserLocation? = null,
    val nearestStation: Pair<StationData, Double>? = null,
    val sortedStations: List<Pair<StationData, Double>> = emptyList(),
    val locationPermissionGranted: Boolean = false,
    val isLocationLoading: Boolean = false
)

/**
 * ViewModel class managing air quality data and application state.
 * 
 * Implements MVVM pattern with reactive state management using StateFlow.
 * Coordinates between Repository layer and UI components.
 */
class AirQualityViewModel : ViewModel() {
    private val repository = AirQualityRepository()
    
    private val _uiState = MutableStateFlow(AirQualityUiState())
    val uiState: StateFlow<AirQualityUiState> = _uiState.asStateFlow()
    
    init {
        loadStations()
    }
    
    fun loadStations() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
            
            repository.getBerlinStations()
                .onSuccess { stations ->
                    _uiState.value = _uiState.value.copy(
                        stations = stations,
                        isLoading = false,
                        lastUpdate = java.text.SimpleDateFormat("HH:mm", java.util.Locale.getDefault())
                            .format(java.util.Date())
                    )
                    
                    // Update sorted stations if user location is available
                    _uiState.value.userLocation?.let { userLoc ->
                        updateLocationBasedData(userLoc.latitude, userLoc.longitude)
                    }
                }
                .onFailure { exception ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = "Failed to load stations: ${exception.message}"
                    )
                }
        }
    }
    
    fun refresh() {
        loadStations()
    }
    
    fun updateUserLocation(location: Location) {
        val userLocation = UserLocation(location.latitude, location.longitude)
        _uiState.value = _uiState.value.copy(
            userLocation = userLocation,
            isLocationLoading = false
        )
        
        // Update location-based data
        updateLocationBasedData(location.latitude, location.longitude)
    }
    
    private fun updateLocationBasedData(latitude: Double, longitude: Double) {
        val currentStations = _uiState.value.stations
        if (currentStations.isNotEmpty()) {
            // Find nearest station
            val nearestStation = LocationUtils.findNearestStation(
                latitude, longitude, currentStations
            )
            
            // Sort all stations by distance
            val sortedStations = LocationUtils.sortStationsByDistance(
                latitude, longitude, currentStations
            )
            
            _uiState.value = _uiState.value.copy(
                nearestStation = nearestStation,
                sortedStations = sortedStations
            )
        }
    }
    
    fun setLocationPermissionStatus(granted: Boolean) {
        _uiState.value = _uiState.value.copy(locationPermissionGranted = granted)
    }
    
    fun setLocationLoading(loading: Boolean) {
        _uiState.value = _uiState.value.copy(isLocationLoading = loading)
    }
    
    fun clearLocationError() {
        // Clear any location-related errors if needed
        if (_uiState.value.errorMessage?.contains("location", ignoreCase = true) == true) {
            _uiState.value = _uiState.value.copy(errorMessage = null)
        }
    }
}
