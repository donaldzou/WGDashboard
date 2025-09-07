<script setup lang="ts">
import LocaleText from "@/components/text/localeText.vue";
import { fetchGet } from "@/utilities/fetch.js"
import {onMounted, ref} from "vue";
const props = defineProps(['selectedPeer'])
const loaded = ref(false)
const endpoints = ref(undefined)
const mapAvailable = ref(undefined)

import "ol/ol.css"
import Map from 'ol/Map.js';
import OSM from 'ol/source/OSM.js';
import TileLayer from 'ol/layer/Tile.js';
import View from 'ol/View.js';
import {Feature} from "ol";
import {fromLonLat} from "ol/proj"
import {LineString, Point} from "ol/geom"
import {linear} from 'ol/easing';
import {Circle, Fill, Stroke, Style, Text} from "ol/style.js";
import {Vector} from "ol/layer"
import {Vector as SourceVector} from "ol/source"

const map = ref(undefined)

const loadEndpoints = async () => {
	await fetchGet("/api/getPeerHistoricalEndpoints", {
		id: props.selectedPeer.id,
		configurationName: props.selectedPeer.configuration.Name
	}, async (res) => {
		if (res.status){
			endpoints.value = res.data
		}
		loaded.value = true
		if (endpoints.value.geolocation){
			try{
				await fetch("https://tile.openstreetmap.org/",
					{ signal: AbortSignal.timeout(1500) })
				mapAvailable.value = true;
				map.value = new Map({
					target: 'map',
					layers: [
						new TileLayer({
							source: new OSM(),
						}),
					],
					view: new View({
						center: fromLonLat([17.64, 16.35]),
						zoom: 0,
					}),
				});
				if (endpoints.value.geolocation){
					const vectorSource = new SourceVector();
					let geo = endpoints.value.geolocation.filter(x => x.lat && x.lon)
					geo.forEach(data => {
						vectorSource.addFeature(new Feature({
							geometry: new Point(fromLonLat([data.lon, data.lat])),
						}))
					})
					vectorSource.addFeature(new Feature({

					}))
					map.value.addLayer(new Vector({
						source: vectorSource,
						style: () => {
							return new Style({
								image: new Circle({
									radius: 10,
									fill: new Fill({ color: '#0d6efd' }),
									stroke: new Stroke({ color: 'white', width: 5 }),
								})
							});
						}
					}));


				}


			}catch (e) {
				console.log(e)
				mapAvailable.value = false
			}

		}
	})
}

onMounted(() => loadEndpoints())
const getGeolocation = (endpoint) => {
	if (endpoints.value.geolocation){
		let geo = endpoints.value.geolocation.find(x => x.query === endpoint)
		if (geo){
			let c = [geo.city, geo.country]
			if (c.filter(x => x !== undefined).length === 0) c.push('Private Address')
			return c.filter(x => x !== undefined).join(", ")
		}
	}
	return undefined
}

const setMapCenter = (endpoint) => {
	if (endpoints.value.geolocation){
		let geo = endpoints.value.geolocation.find(x => x.query === endpoint)
		if (geo && geo.lon && geo.lat){
			map.value.getView().animate({zoom: 4}, {center: fromLonLat([
					geo.lon, geo.lat
				])}, {easing: linear})
		}
	}
}

</script>

<template>
	<div class="card rounded-3 bg-transparent">
		<div class="card-header text-muted">
			<LocaleText t="Peer Historical Endpoints"></LocaleText>
		</div>
		<div class="card-body">
			<div class="bg-body-tertiary p-3 d-flex rounded-3">
				<div class="m-auto" v-if="!loaded">
					<span class="spinner-border spinner-border-sm me-2"></span><LocaleText t="Loading..."></LocaleText>
				</div>
				<div v-else class="w-100 d-flex flex-column gap-3">
					<div class="bg-body d-flex  w-100 rounded-3" style="height: 500px" id="map">
						<div class="m-auto" v-if="!mapAvailable">
							<div v-if="mapAvailable === undefined">
								<span class="spinner-border spinner-border-sm me-2"></span>
								<LocaleText t="Loading Map..."></LocaleText>
							</div>
							<div v-if="mapAvailable === false" class="text-muted">
								<LocaleText t="Map is not available"></LocaleText>
							</div>
						</div>
					</div>
					<table class="table table-hover">
						<thead>
							<tr>
								<th>Endpoint</th>
								<th v-if="endpoints.geolocation">Geolocation</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="endpoint in endpoints.endpoints"
								@click="setMapCenter(endpoint.endpoint)"
								style="cursor: pointer">
								<td>
									{{ endpoint.endpoint }}
								</td>
								<td v-if="endpoints.geolocation">
									{{ getGeolocation(endpoint.endpoint) }}
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>

</style>