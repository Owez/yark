<script lang="ts">
	import { VisXYContainer, VisStackedBar, VisAxis } from '@unovis/svelte';
	import { elementWasUpdated, type Element } from '$lib/element';

	export let trackedElement: Element;

	/**
	 * Record of a single graph point
	 */
	type GraphRecord = {
		x: Date;
		y: number;
	};

	/**
	 * Converts an element to an array of graph records
	 * @param element Element to convert
	 */
	function elementToGraphRecord(element: Element): GraphRecord[] {
		let records: GraphRecord[] = [];
		Object.entries(element).forEach((entry) => {
			const [isoString, value] = entry;
			const date = new Date(isoString);
			records.push({ x: date, y: value });
		});
		console.log(records);
		return records;
	}

	const x = (d: GraphRecord) => d.x.getTime();
	const y = (d: GraphRecord) => d.y;

	$: graphData = elementToGraphRecord(trackedElement);
</script>

{#if elementWasUpdated(trackedElement)}
	<h2 class="video">Views over time</h2>
	<div class="graph">
		<VisXYContainer data={graphData}>
			<VisStackedBar {x} {y} barWidth={10} />
			<VisAxis type="x" />
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
