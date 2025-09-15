package de.project.air_quality_app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.material3.MaterialTheme
import de.project.air_quality_app.viewmodel.AirQualityViewModel
import com.mapbox.geojson.Point
import com.mapbox.maps.*
import com.mapbox.maps.plugin.annotation.annotations
import com.mapbox.maps.plugin.annotation.generated.*

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                AirQualityMapScreen()
            }
        }
    }
}

@Composable
fun AirQualityMapScreen(
    viewModel: AirQualityViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var selectedStation by remember { mutableStateOf<de.project.air_quality_app.models.StationData?>(null) }
    
    Box(modifier = Modifier.fillMaxSize()) {
        // Map View
        AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { context ->
                val mapInitOptions = MapInitOptions(
                    context = context, 
                    styleUri = "mapbox://styles/mapbox/dark-v10"
                )
                MapView(context, mapInitOptions).apply {
                    this.mapboxMap.setCamera(
                        CameraOptions.Builder()
                            .center(Point.fromLngLat(13.4050, 52.52)) // Berlin center
                            .zoom(10.0)
                            .build()
                    )
                }
            },
            update = { mapView ->
                // Update markers when stations data changes
                if (uiState.stations.isNotEmpty()) {
                    updateMapMarkers(mapView, uiState.stations) { station ->
                        selectedStation = station
                    }
                }
            }
        )
        
        // Status overlay
        Card(
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(16.dp),
            shape = RoundedCornerShape(8.dp),
            colors = CardDefaults.cardColors(
                containerColor = Color.Black.copy(alpha = 0.8f)
            )
        ) {
            Column(
                modifier = Modifier.padding(12.dp)
            ) {
                Text(
                    text = "Berlin Air Quality",
                    style = MaterialTheme.typography.titleMedium,
                    color = Color.White,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${uiState.stations.size} stations",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray
                )
                if (uiState.lastUpdate != null) {
                    Text(
                        text = "Updated: ${uiState.lastUpdate}",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.Gray
                    )
                }
            }
        }
        
        // Loading indicator
        if (uiState.isLoading) {
            Card(
                modifier = Modifier
                    .align(Alignment.Center)
                    .padding(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.Black.copy(alpha = 0.8f)
                )
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = Color.White
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "Loading stations...",
                        color = Color.White
                    )
                }
            }
        }
        
        // Error message
        if (uiState.errorMessage != null) {
            Card(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.Red.copy(alpha = 0.9f)
                )
            ) {
                Column(
                    modifier = Modifier.padding(12.dp)
                ) {
                    Text(
                        text = "Error",
                        style = MaterialTheme.typography.titleSmall,
                        color = Color.White,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = uiState.errorMessage ?: "Unknown error",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.White
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Button(
                        onClick = { viewModel.refresh() },
                        colors = ButtonDefaults.buttonColors(
                            containerColor = Color.White,
                            contentColor = Color.Red
                        )
                    ) {
                        Text("Retry")
                    }
                }
            }
        }
        
        // Station Details Card (angezeigt wenn Station ausgewählt)
        selectedStation?.let { station ->
            Card(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth()
                    .padding(16.dp),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color.White
                ),
                elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = station.getDisplayName(),
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.weight(1f)
                        )
                        IconButton(
                            onClick = { selectedStation = null }
                        ) {
                            Text("✕", style = MaterialTheme.typography.titleLarge)
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    // AQI Hauptwert
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Card(
                            colors = CardDefaults.cardColors(
                                containerColor = Color(station.getAqiColor())
                            ),
                            modifier = Modifier.size(48.dp)
                        ) {
                            Box(
                                contentAlignment = Alignment.Center,
                                modifier = Modifier.fillMaxSize()
                            ) {
                                Text(
                                    text = station.aqi?.toString() ?: "N/A",
                                    color = Color.White,
                                    fontWeight = FontWeight.Bold,
                                    style = MaterialTheme.typography.titleMedium
                                )
                            }
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Column {
                            Text(
                                text = "AQI: ${station.getAqiDescription()}",
                                style = MaterialTheme.typography.titleSmall,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "Luftqualitätsindex",
                                style = MaterialTheme.typography.bodySmall,
                                color = Color.Gray
                            )
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(12.dp))
                    
                    // Messwerte Grid
                    LazyVerticalGrid(
                        columns = GridCells.Fixed(2),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.heightIn(max = 200.dp)
                    ) {
                        // PM2.5
                        if (station.pm25 != null) {
                            item {
                                MeasurementCard("PM2.5", "${station.pm25}", "µg/m³")
                            }
                        }
                        // PM10
                        if (station.pm10 != null) {
                            item {
                                MeasurementCard("PM10", "${station.pm10}", "µg/m³")
                            }
                        }
                        // NO2
                        if (station.no2 != null) {
                            item {
                                MeasurementCard("NO₂", "${station.no2}", "µg/m³")
                            }
                        }
                        // O3
                        if (station.o3 != null) {
                            item {
                                MeasurementCard("O₃", "${station.o3}", "µg/m³")
                            }
                        }
                        // Temperature
                        if (station.temperature != null) {
                            item {
                                MeasurementCard("Temp", "${station.temperature}", "°C")
                            }
                        }
                        // Humidity
                        if (station.humidity != null) {
                            item {
                                MeasurementCard("Luftf.", "${station.humidity.toInt()}", "%")
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun MeasurementCard(label: String, value: String, unit: String) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = Color.Gray.copy(alpha = 0.1f)
        ),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = label,
                style = MaterialTheme.typography.labelSmall,
                color = Color.Gray
            )
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Text(
                text = unit,
                style = MaterialTheme.typography.labelSmall,
                color = Color.Gray
            )
        }
    }
}

private fun updateMapMarkers(
    mapView: MapView, 
    stations: List<de.project.air_quality_app.models.StationData>,
    onStationClick: (de.project.air_quality_app.models.StationData) -> Unit
) {
    val annotationApi = mapView.annotations
    val pointAnnotationManager = annotationApi.createPointAnnotationManager()
    
    // Clear existing markers
    pointAnnotationManager.deleteAll()
    
    // Add new markers for each station
    stations.forEach { station ->
        val pointAnnotationOptions = PointAnnotationOptions()
            .withPoint(Point.fromLngLat(station.longitude, station.latitude))
            .withTextField(station.getDisplayName())
            .withTextSize(10.0)
            .withTextColor(android.graphics.Color.WHITE)
            .withTextHaloColor(android.graphics.Color.BLACK)
            .withTextHaloWidth(2.0)
            .withIconSize(1.5)
            .withIconColor(station.getAqiColor())
        
        val pointAnnotation = pointAnnotationManager.create(pointAnnotationOptions)
        
        // Add click listener
        pointAnnotationManager.addClickListener { clickedAnnotation ->
            if (clickedAnnotation.id == pointAnnotation.id) {
                onStationClick(station)
                true
            } else {
                false
            }
        }
    }
}