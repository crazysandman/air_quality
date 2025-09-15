package de.project.air_quality_app.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import de.project.air_quality_app.models.StationData
import de.project.air_quality_app.repository.AirQualityRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class AirQualityUiState(
    val stations: List<StationData> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
    val lastUpdate: String? = null
)

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
}
