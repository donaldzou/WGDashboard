<script>
import {fetchGet} from "@/utilities/fetch.js";
import Peer from "@/components/configurationComponents/peer.vue";
import { Line, Bar } from 'vue-chartjs'
import Fuse from "fuse.js";
import {
	Chart,
	ArcElement,
	LineElement,
	BarElement,
	PointElement,
	BarController,
	BubbleController,
	DoughnutController,
	LineController,
	PieController,
	PolarAreaController,
	RadarController,
	ScatterController,
	CategoryScale,
	LinearScale,
	LogarithmicScale,
	RadialLinearScale,
	TimeScale,
	TimeSeriesScale,
	Decimation,
	Filler,
	Legend,
	Title,
	Tooltip
} from 'chart.js';

Chart.register(
	ArcElement,
	LineElement,
	BarElement,
	PointElement,
	BarController,
	BubbleController,
	DoughnutController,
	LineController,
	PieController,
	PolarAreaController,
	RadarController,
	ScatterController,
	CategoryScale,
	LinearScale,
	LogarithmicScale,
	RadialLinearScale,
	TimeScale,
	TimeSeriesScale,
	Decimation,
	Filler,
	Legend,
	Title,
	Tooltip
);

import dayjs from "dayjs";
import PeerSearch from "@/components/configurationComponents/peerSearch.vue";
import {DashboardConfigurationStore} from "@/stores/DashboardConfigurationStore.js";
import {ref} from "vue";
import {WireguardConfigurationsStore} from "@/stores/WireguardConfigurationsStore.js";
import PeerList from "@/components/configurationComponents/peerList.vue";

export default {
	name: "configuration",
	components: {PeerList},
}
</script>

<template>
	<div class="mt-5 text-body">
<!--		<PeerList></PeerList>-->
		<RouterView v-slot="{ Component }">
			<Transition name="fade2" mode="out-in">
				<Component :is="Component"></Component>
			</Transition>
		</RouterView>
	</div>
</template>

<style scoped>
	
</style>