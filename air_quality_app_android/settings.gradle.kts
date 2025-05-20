pluginManagement {
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven {
            url = uri("https://api.mapbox.com/downloads/v2/releases/maven")
            credentials {
                username = "mapbox"
                password = "sk.eyJ1IjoiY3JhenlzYW5kbWFuIiwiYSI6ImNtYXRtcGZjNDBvY3Mya3M0djRxOTNodHEifQ.vusiX0wneU0q3nCV5rufQw"
            }
        }
    }
}

rootProject.name = "air_quality_app"
include(":app")
 