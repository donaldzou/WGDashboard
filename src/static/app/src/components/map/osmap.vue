<script>
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

export default {
	name: "osmap",
	props: {
		type: "",
		d: Object || Array
	},
	data(){
		return {
			osmAvailable: true
		}
	},
	setup(){
		const store = DashboardConfigurationStore();
		return {
			store
		}
	},
	methods: {
		getLastLonLat(){
			if (this.type === 'traceroute'){
				const k = this.d.findLast(data => data.geo && data.geo.lat && data.geo.lon)
				if (k){
					return [k.geo.lon, k.geo.lat]
				}
				return [0,0]
			}
			return [this.d.geo.lon, this.d.geo.lat]
		}	
	},
	async mounted() {
		const osm = await fetch("https://tile.openstreetmap.org/", 
			{ signal: AbortSignal.timeout(1500) })
			.then(res => {
				const map = new Map({
					target: 'map',
					layers: [
						new TileLayer({
							source: new OSM(),
						}),
					],
					view: new View({
						center: fromLonLat(this.getLastLonLat()),
						zoom: this.type === 'traceroute' ? 3:10,
					}),
				});
				const coordinates = [];
				const vectorSource = new SourceVector();
				if (this.type === 'traceroute'){
					this.d.forEach(data => {
						if (data.geo && data.geo.lat && data.geo.lon) {
							const coordinate = fromLonLat([data.geo.lon, data.geo.lat]);
							coordinates.push(coordinate);
							const l = this.getLastLonLat();
							const marker = new Feature({
								geometry: new Point(coordinate),
								last: data.geo.lon === l[0] && data.geo.lat === l[1]
							});
							vectorSource.addFeature(marker);
						}
					})
				}
				else{
					const coordinate = fromLonLat([this.d.geo.lon, this.d.geo.lat])
					coordinates.push(coordinate);
					const marker = new Feature({
						geometry: new Point(coordinate)
					});
					vectorSource.addFeature(marker);
				}
				const lineString = new LineString(coordinates);
				const lineFeature = new Feature({
					geometry: lineString
				});
				console.log(lineString)
				vectorSource.addFeature(lineFeature);
				const vectorLayer = new Vector({
					source: vectorSource,
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
				if (this.store.Configuration.Server.dashboard_theme === 'dark'){
					map.on('postcompose',() => {
						document.querySelector('#map').style.filter="grayscale(80%) invert(100%)";
					});
				}
			}).catch(e => {
				this.osmAvailable = false
			})
	}
}
</script>

<template>
	<div id="map" class="w-100 rounded-3" v-if="this.osmAvailable"></div>
</template>

<style>
.ol-layer canvas{
	border-radius: var(--bs-border-radius-lg) !important;
}

#map{
	height: 300px;
}
</style>