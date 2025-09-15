package de.project.air_quality_app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
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
import de.project.air_quality_app.ui.theme.AirQualityAppTheme
import de.project.air_quality_app.viewmodel.AirQualityViewModel
import com.mapbox.geojson.Point
import com.mapbox.maps.*
import com.mapbox.maps.plugin.annotation.annotations
import com.mapbox.maps.plugin.annotation.generated.*

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AirQualityAppTheme {
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
                    updateMapMarkers(mapView, uiState.stations)
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
                        text = uiState.errorMessage,
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
    }
}

private fun updateMapMarkers(mapView: MapView, stations: List<de.project.air_quality_app.models.StationData>) {
    val annotationApi = mapView.annotations
    val pointAnnotationManager = annotationApi.createPointAnnotationManager()
    
    // Clear existing markers
    pointAnnotationManager.deleteAll()
    
    // Add new markers for each station
    stations.forEach { station ->
        val pointAnnotationOptions = PointAnnotationOptions()
            .withPoint(Point.fromLngLat(station.longitude, station.latitude))
            .withTextField(station.getDisplayName())
            .withTextSize(12.0)
            .withTextColor(android.graphics.Color.WHITE)
            .withTextHaloColor(android.graphics.Color.BLACK)
            .withTextHaloWidth(2.0)
            .withIconSize(1.2)
        
        pointAnnotationManager.create(pointAnnotationOptions)
    }
}