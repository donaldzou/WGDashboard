<script setup>
import "ol/ol.css"
import Map from 'ol/Map.js';
import OSM from 'ol/source/OSM.js';
import TileLayer from 'ol/layer/Tile.js';
import View from 'ol/View.js';
import {Feature} from "ol";
import {fromLonLat} from "ol/proj"
import {LineString, Point} from "ol/geom"
import {Circle, Fill, Stroke, Style, Text} from "ol/style.js";
import {Vector} from "ol/layer"
import {Vector as SourceVector} from "ol/source"
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {computed, onMounted, ref, watch} from "vue";
import LocaleText from "@/components/text/localeText.vue";
const store = DashboardConfigurationStore()
const props = defineProps({
	type: "",
	d: Object || Array
})
const osmAvailable = ref(false)

await fetch("https://tile.openstreetmap.org/", {
	signal: AbortSignal.timeout(1500)
})
.then(() => {
	osmAvailable.value = true
})
.catch((e) => {
	console.log(e)
})
if (osmAvailable.value){
	const mapView = new View({
		center: fromLonLat([179.47, 57.89]),
		zoom: 1,
	})
	const map = new Map({
		layers: [
			new TileLayer({
				source: new OSM(),
			}),
		],
		view: mapView,
	});
	const vectorLayer = new Vector({
		style: function(feature) {
			if (feature.getGeometry().getType() === 'Point') {
				return new Style({
					image: new Circle({
						radius: 10,
						fill: new Fill({ color: feature.get("last") ? '#dc3545':'#0d6efd' }),
						stroke: new Stroke({ color: 'white', width: 5 }),
					})
				});
			} else if (feature.getGeometry().getType() === 'LineString') {
				return new Style({
					stroke: new Stroke({
						color: '#0d6efd',
						width: 2
					})
				});
			}
		}
	});
	map.addLayer(vectorLayer);
	onMounted(() => {
		map.setTarget('map')
		if (store.Configuration.Server.dashboard_theme === 'dark'){
			map.on('postcompose',() => {
				document.querySelector('#map').style.filter="grayscale(80%) invert(100%)";
			});
		}
	})
	let sourceVector = new SourceVector()
	let cords = []
	let lineString = new LineString(cords)
	let lineStringFeature = new Feature({
		geometry: lineString
	})
	
	sourceVector.addFeature(lineStringFeature)
	let ips = ref([])
	vectorLayer.setSource(sourceVector);
	watch(() => {
		return props.d
	}, (newData) => {
		if (newData.length > 0){
			let latestResultItem = newData[newData.length - 1]
			if (latestResultItem.geo && latestResultItem.geo.status === 'success'){
				let cord = fromLonLat([latestResultItem.geo.lon, latestResultItem.geo.lat])
				if (!ips.value.find(x => x === latestResultItem.address)){
					cords.push(cord)
					lineString.setCoordinates(cords)
					lineStringFeature.setGeometry(lineString)
					sourceVector.removeFeature(lineStringFeature)
					sourceVector.addFeature(lineStringFeature)
					sourceVector.addFeature(new Feature({
						geometry: new Point(cord),
						last: false,
					}));
					ips.value.push(latestResultItem.address)
				}
				mapView.animate({ center: cord })
				mapView.animate({ zoom: 10 })
			}
		}else {
			sourceVector.clear()
			cords = []
			ips.value = []
		}
	},{
		deep: true,
	})
}
</script>

<template>
	<div class="bg-body-secondary rounded-3 mb-3 d-flex animate__animated animate__fadeIn"
	     v-if="!osmAvailable"
	     style="height: 300px"
	>
		<div class="m-auto">
			<small class="text-muted">
				<LocaleText t="Sorry, OpenStreetMap is not available"></LocaleText>
			</small>
		</div>
	</div>

	<div id="map" class="w-100 rounded-3" v-else></div>
</template>

<style scoped>
.ol-layer canvas{
	border-radius: var(--bs-border-radius-lg) !important;
}

#map{
	height: 300px;
}
</style>