package de.project.air_quality_app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView
import com.example.air_quality_app.ui.theme.AirQualityAppTheme
import com.mapbox.geojson.Point
import com.mapbox.maps.MapInitOptions
import com.mapbox.maps.MapView
import com.mapbox.maps.CameraOptions


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AirQualityAppTheme {
                MapViewScreen()
            }
        }
    }
}

@Composable
fun MapViewScreen() {
    AndroidView(
        modifier = Modifier.fillMaxSize(),
        factory = { context ->
            val mapInitOptions = MapInitOptions(context, styleUri = "mapbox://styles/mapbox/streets-v12")
            MapView(context, mapInitOptions).apply {
                this.mapboxMap.setCamera(
                    CameraOptions.Builder()
                        .center(Point.fromLngLat(13.4050, 52.52)) // Berlin
                        .zoom(10.0)
                        .build()
                )
            }
        }
    )
}