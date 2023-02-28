<script lang="ts">
	import { VisXYContainer, VisStackedBar, VisAxis } from '@unovis/svelte';
	import { elementWasUpdated, type Element } from '$lib/element';
	import { humanDateFromIso } from '$lib/utils';

	export let trackedElement: Element;

	// Date tick formatting, containing an array of human times corresponding to ticks generated
	let dateTicks: string[] = [];

	/**
	 * Record of a single graph point with x being ticks from 0 to x, and y being the value
	 */
	type GraphRecord = {
		x: number;
		y: any;
	};

	/**
	 * Converts an element to an array of graph records
	 * @param element Element to convert
	 */
	function elementToGraphRecord(element: Element): GraphRecord[] {
		let records: GraphRecord[] = [];
		const entries = Object.entries(element);
		for (let index = 0; index < entries.length; index++) {
			const [isoString, value] = entries[index];
			dateTicks.push(humanDateFromIso(isoString));
			records.push({ x: index, y: value });
		}
		return records;
	}

	// Conversion of graph record to ticks
	const x = (d: GraphRecord) => d.x;
	const y = (d: GraphRecord) => d.y;

	// Tick formatting (x-axis labels)
	const tickFormat = (tick: number) => dateTicks[tick];

	$: graphData = elementToGraphRecord(trackedElement);
</script>

{#if elementWasUpdated(trackedElement)}
	<h2 class="video">Views over time</h2>
	<div class="graph">
		<VisXYContainer data={graphData}>
			<VisStackedBar {x} {y} />
			<VisAxis type="x" {tickFormat} />
			<VisAxis type="y" />
		</VisXYContainer>
	</div>
{/if}

<style lang="scss">
	$large: 1300px;

	.graph {
		margin-top: 0.75rem;
	}

	@media (max-width: $large) {
		.graph {
			width: 40rem;
		}
	}

	@media (min-width: $large) {
		.graph {
			width: 55rem;
		}
	}
</style>
