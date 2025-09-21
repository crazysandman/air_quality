/**
 * Air Quality Monitoring App - Main Activity
 * ==========================================
 * 
 * Primary Android activity implementing a comprehensive air quality monitoring
 * interface using Jetpack Compose, Mapbox SDK, and Google Location Services.
 * 
 * Key Features:
 * - Interactive map with air quality station markers
 * - Real-time GPS location tracking
 * - Color-coded AQI (Air Quality Index) visualization
 * - Detailed station information display
 * - Permission handling for location services
 * 
 * Architecture:
 * - MVVM pattern with ViewModel and LiveData
 * - Repository pattern for data management
 * - Dependency injection ready structure
 */

package de.project.air_quality_app

// Android Framework Imports
import android.Manifest
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.os.Bundle

// AndroidX and Jetpack Compose Imports
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.MyLocation
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.material3.MaterialTheme

// Project-specific Imports
import de.project.air_quality_app.location.LocationManager
import de.project.air_quality_app.utils.LocationUtils
import de.project.air_quality_app.viewmodel.AirQualityViewModel

// Mapbox SDK Imports
import com.mapbox.geojson.Point
import com.mapbox.maps.*
import com.mapbox.maps.plugin.annotation.annotations
import com.mapbox.maps.plugin.annotation.generated.*
import kotlinx.coroutines.launch

/**
 * Main Activity Class
 * 
 * Serves as the entry point for the Air Quality Monitoring application.
 * Initializes the Compose UI and sets up the main theme.
 */
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

/**
 * Main Air Quality Map Screen Composable
 * 
 * Primary UI component that displays an interactive map with air quality data.
 * Integrates Mapbox for mapping, custom markers for stations, and location services.
 * 
 * Features implemented:
 * - Interactive Mapbox map with dark theme
 * - Custom AQI markers with color-coded values
 * - GPS location tracking with permission handling
 * - Station detail cards with comprehensive air quality data
 * - Loading states and error handling
 * - Responsive UI layout with proper spacing
 * 
 * @param viewModel Air quality data and state management
 */
@Composable
fun AirQualityMapScreen(
    viewModel: AirQualityViewModel = viewModel()
) {
    // Compose state management
    val context = LocalContext.current
    val uiState by viewModel.uiState.collectAsState()
    var selectedStation by remember { mutableStateOf<de.project.air_quality_app.models.StationData?>(null) }
    var mapView by remember { mutableStateOf<MapView?>(null) }
    
    // Location manager
    val locationManager = remember { LocationManager(context) }
    val scope = rememberCoroutineScope()
    
    // Permission launcher
    val locationPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val granted = permissions.values.any { it }
        viewModel.setLocationPermissionStatus(granted)
        
        if (granted) {
            // Get current location when permission is granted
            scope.launch {
                viewModel.setLocationLoading(true)
                try {
                    val location = locationManager.getCurrentLocation()
                    if (location != null) {
                        viewModel.updateUserLocation(location)
                        // Center map on user location
                        mapView?.mapboxMap?.setCamera(
                            CameraOptions.Builder()
                                .center(Point.fromLngLat(location.longitude, location.latitude))
                                .zoom(14.0)
                                .build()
                        )
                    } else {
                        viewModel.setLocationLoading(false)
                    }
                } catch (e: Exception) {
                    viewModel.setLocationLoading(false)
                }
            }
        }
    }
    
    // Check permission on first launch
    LaunchedEffect(Unit) {
        viewModel.setLocationPermissionStatus(locationManager.hasLocationPermission())
    }
    
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
                    mapView = this
                }
            },
            update = { mapViewInstance ->
                mapView = mapViewInstance
                // Update markers when stations data changes
                if (uiState.stations.isNotEmpty()) {
                    updateMapMarkers(mapViewInstance, uiState.stations, uiState.userLocation) { station ->
                        selectedStation = station
                    }
                }
            }
        )
        
        // Status overlay
        Card(
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(40.dp),
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
                
                // Nearest station info
                uiState.nearestStation?.let { (station, distance) ->
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Nearest: ${station.getDisplayName()}",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.White,
                        fontWeight = FontWeight.Medium
                    )
                    Text(
                        text = "${LocationUtils.formatDistance(distance)} away",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color.Gray
                    )
                }
            }
        }
        
        // Location button (moved to bottom)
        FloatingActionButton(
            onClick = {
                if (uiState.locationPermissionGranted) {
                    scope.launch {
                        viewModel.setLocationLoading(true)
                        try {
                            val location = locationManager.getCurrentLocation()
                            if (location != null) {
                                viewModel.updateUserLocation(location)
                                // Center map on user location
                                mapView?.mapboxMap?.setCamera(
                                    CameraOptions.Builder()
                                        .center(Point.fromLngLat(location.longitude, location.latitude))
                                        .zoom(14.0)
                                        .build()
                                )
                            } else {
                                // Handle case where location is null
                                viewModel.setLocationLoading(false)
                                // Could show a toast or error message here
                            }
                        } catch (e: Exception) {
                            viewModel.setLocationLoading(false)
                            // Handle error
                        }
                    }
                } else {
                    locationPermissionLauncher.launch(LocationManager.REQUIRED_PERMISSIONS)
                }
            },
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(40.dp),
            containerColor = if (uiState.locationPermissionGranted)
                MaterialTheme.colorScheme.primary else Color.Gray
        ) {
            if (uiState.isLocationLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = Color.White,
                    strokeWidth = 2.dp
                )
            } else {
                Icon(
                    imageVector = if (uiState.userLocation != null) Icons.Default.MyLocation else Icons.Default.LocationOn,
                    contentDescription = "My Location",
                    tint = Color.White
                )
            }
        }
        
        // Loading indicator
        if (uiState.isLoading) {
            Card(
                modifier = Modifier
                    .align(Alignment.Center)
                    .padding(40.dp),
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
                    .padding(40.dp),
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
                    .padding(40.dp),
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

/**
 * Creates a custom location icon for user's GPS position.
 * 
 * Generates a programmatic bitmap icon representing the user's current location
 * with a blue color scheme and circular design for clear visibility on map.
 * 
 * @param context Android context for resource access
 * @return Bitmap icon suitable for map annotation
 */
fun createLocationIcon(context: android.content.Context): Bitmap {
    val size = 60 // Icon dimensions in pixels
    val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(bitmap)
    
    // Paint configurations for different icon elements
    val outerPaint = Paint().apply {
        color = android.graphics.Color.WHITE
        isAntiAlias = true
        style = Paint.Style.FILL
    }
    val borderPaint = Paint().apply {
        color = android.graphics.Color.BLUE
        isAntiAlias = true
        style = Paint.Style.STROKE
        strokeWidth = 4f
    }
    val innerPaint = Paint().apply {
        color = android.graphics.Color.BLUE
        isAntiAlias = true
        style = Paint.Style.FILL
    }
    
    // Calculate positioning for centered circles
    val centerX = size / 2f
    val centerY = size / 2f
    val outerRadius = size / 2f - 4f
    val innerRadius = size / 6f
    
    // Draw layered circles: outer white circle with blue border and inner blue dot
    canvas.drawCircle(centerX, centerY, outerRadius, outerPaint)
    canvas.drawCircle(centerX, centerY, outerRadius, borderPaint)
    canvas.drawCircle(centerX, centerY, innerRadius, innerPaint)
    
    return bitmap
}

/**
 * Creates color-coded AQI (Air Quality Index) icons for station markers.
 * 
 * Generates rectangular badges displaying AQI values with color-coding
 * based on air quality levels (Good/Moderate/Unhealthy/etc.).
 * 
 * @param context Android context for resource access
 * @param aqi Air Quality Index value (0-500+)
 * @param aqiColor Background color based on AQI category
 * @return Bitmap icon with AQI value and appropriate color coding
 */
fun createAqiIcon(context: android.content.Context, aqi: Int?, aqiColor: Int): Bitmap {
    val width = 120   // Icon width in pixels
    val height = 80   // Icon height in pixels
    val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
    val canvas = Canvas(bitmap)
    
    // Background paint (rounded rectangle)
    val backgroundPaint = Paint().apply {
        color = aqiColor
        isAntiAlias = true
        style = Paint.Style.FILL
    }
    
    // Border paint
    val borderPaint = Paint().apply {
        color = android.graphics.Color.WHITE
        isAntiAlias = true
        style = Paint.Style.STROKE
        strokeWidth = 3f
    }
    
    // Text paint
    val textPaint = Paint().apply {
        color = android.graphics.Color.WHITE
        isAntiAlias = true
        textAlign = Paint.Align.CENTER
        textSize = 28f
        isFakeBoldText = true
    }
    
    val cornerRadius = 12f
    val rect = android.graphics.RectF(3f, 3f, width - 3f, height - 3f)
    
    // Draw rounded rectangle background
    canvas.drawRoundRect(rect, cornerRadius, cornerRadius, backgroundPaint)
    canvas.drawRoundRect(rect, cornerRadius, cornerRadius, borderPaint)
    
    // Draw AQI text
    val aqiText = aqi?.toString() ?: "N/A"
    val centerX = width / 2f
    val centerY = height / 2f + textPaint.textSize / 3f
    canvas.drawText(aqiText, centerX, centerY, textPaint)
    
    return bitmap
}

private fun updateMapMarkers(
    mapView: MapView, 
    stations: List<de.project.air_quality_app.models.StationData>,
    userLocation: de.project.air_quality_app.viewmodel.UserLocation?,
    onStationClick: (de.project.air_quality_app.models.StationData) -> Unit
) {
    val annotationApi = mapView.annotations
    val pointAnnotationManager = annotationApi.createPointAnnotationManager()
    
    // Clear existing markers
    pointAnnotationManager.deleteAll()
    
    // Add user location marker if available
    userLocation?.let { location ->
        // Create custom location icon
        val locationIcon = createLocationIcon(mapView.context)
        
        val userAnnotationOptions = PointAnnotationOptions()
            .withPoint(Point.fromLngLat(location.longitude, location.latitude))
            .withIconImage(locationIcon)
            .withIconSize(1.0)
        
        pointAnnotationManager.create(userAnnotationOptions)
    }
    
    // Add new markers for each station with AQI boxes
    stations.forEach { station ->
        val aqiValue = station.aqi
        val aqiColor = getAqiColor(aqiValue)
        val aqiIcon = createAqiIcon(mapView.context, aqiValue, aqiColor)
        
        val pointAnnotationOptions = PointAnnotationOptions()
            .withPoint(Point.fromLngLat(station.longitude, station.latitude))
            .withIconImage(aqiIcon)
            .withIconSize(1.0)
        
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

/**
 * Determines appropriate color coding for Air Quality Index values.
 * 
 * Implements the standard EPA AQI color scheme for visual representation
 * of air quality levels from Good (green) to Hazardous (maroon).
 * 
 * AQI Categories and Colors:
 * - 0-50: Good (Green) - Air quality is satisfactory
 * - 51-100: Moderate (Yellow) - Acceptable for most people
 * - 101-150: Unhealthy for Sensitive Groups (Orange)
 * - 151-200: Unhealthy (Red) - Everyone may experience health effects
 * - 201-300: Very Unhealthy (Purple) - Health alert
 * - 301+: Hazardous (Maroon) - Emergency conditions
 * 
 * @param aqi Air Quality Index value, null if unavailable
 * @return Android Color integer for the appropriate AQI category
 */
fun getAqiColor(aqi: Int?): Int {
    return when (aqi) {
        in 0..50 -> android.graphics.Color.rgb(0, 228, 0)      // Good - Green
        in 51..100 -> android.graphics.Color.rgb(255, 255, 0)  // Moderate - Yellow
        in 101..150 -> android.graphics.Color.rgb(255, 126, 0) // Unhealthy for Sensitive - Orange
        in 151..200 -> android.graphics.Color.rgb(255, 0, 0)   // Unhealthy - Red
        in 201..300 -> android.graphics.Color.rgb(143, 63, 151) // Very Unhealthy - Purple
        in 301..Int.MAX_VALUE -> android.graphics.Color.rgb(126, 0, 35) // Hazardous - Maroon
        else -> android.graphics.Color.GRAY // Unknown/No Data Available
    }
}
